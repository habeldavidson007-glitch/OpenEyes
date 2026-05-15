"""
openeyes/pipeline/orchestrator.py

OpenEyesPipeline: Main orchestration layer that unifies all pipeline components.
Provides a single, clean interface for query processing.
"""

import os
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PipelineResponse:
    answer: str
    status: str
    confidence: float
    domain: str
    fragments_used: int
    response_time_ms: float
    metadata: Dict

class OpenEyesPipeline:
    """
    Unified pipeline orchestrator that provides:
    - Single entry point for all queries
    - Automatic component initialization
    - Performance monitoring
    - Error handling and fallbacks
    - Consistent response format
    
    This replaces the complex multi-module engine with a streamlined interface.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for efficient resource usage."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._retriever = None
        self._processor = None
        self._ingestor = None
        self._initialized = True
        
        # Configuration
        self.verbose = os.getenv('OPENEYES_VERBOSE', '0') == '1'
        self.use_live_fetch = os.getenv('OPENEYES_LIVE_FETCH', '1') == '1'
        self.max_fragments = int(os.getenv('OPENEYES_MAX_FRAGMENTS', '10'))
    
    @property
    def retriever(self):
        if self._retriever is None:
            from .retriever import UnifiedRetriever
            self._retriever = UnifiedRetriever()
        return self._retriever
    
    @property
    def processor(self):
        if self._processor is None:
            from .processor import QueryProcessor
            self._processor = QueryProcessor()
        return self._processor
    
    @property
    def ingestor(self):
        if self._ingestor is None:
            from .ingestor import KnowledgeIngestor
            self._ingestor = KnowledgeIngestor()
        return self._ingestor
    
    def answer(self, query: str, domain: str = 'general') -> PipelineResponse:
        """
        Main query interface - process a query and return a structured response.
        
        Pipeline flow:
        1. Retrieve relevant fragments (local + live if needed)
        2. Process and synthesize answer
        3. Return formatted response with metadata
        
        Args:
            query: User's question
            domain: Domain category (medical, investment, healthcare, economy, etc.)
        
        Returns:
            PipelineResponse with answer, status, confidence, and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve fragments
            retrieval_result = self.retriever.retrieve(
                query=query,
                domain=domain,
                max_results=self.max_fragments,
                use_live=self.use_live_fetch
            )
            
            if self.verbose:
                logger.info(f"Retrieved {len(retrieval_result.fragments)} fragments from {retrieval_result.source}")
            
            # Step 2: Process and synthesize
            process_result = self.processor.process(
                query=query,
                domain=domain,
                fragments=retrieval_result.fragments
            )
            
            # Step 3: Build response
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return PipelineResponse(
                answer=process_result.answer,
                status=process_result.status,
                confidence=process_result.confidence,
                domain=domain,
                fragments_used=process_result.fragments_used,
                response_time_ms=response_time,
                metadata={
                    'retrieval_source': retrieval_result.source,
                    'total_fragments_found': retrieval_result.metadata.get('total_found', 0),
                    'local_count': retrieval_result.metadata.get('local_count', 0),
                    'live_count': retrieval_result.metadata.get('live_count', 0),
                    'processing_metadata': process_result.metadata
                }
            )
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            response_time = (time.time() - start_time) * 1000
            
            return PipelineResponse(
                answer=f"An error occurred while processing your query: {str(e)}",
                status='ERROR',
                confidence=0.0,
                domain=domain,
                fragments_used=0,
                response_time_ms=response_time,
                metadata={'error': str(e)}
            )
    
    def answer_with_ingestion(self, query: str, domain: str = 'general') -> PipelineResponse:
        """
        Answer a query with on-demand ingestion if insufficient data exists.
        
        This is useful for queries about recent events or topics not in the knowledge base.
        """
        # First try normal answer
        response = self.answer(query, domain)
        
        # If insufficient data, try to ingest fresh content
        if response.status == 'INSUFFICIENT_DATA' and self.use_live_fetch:
            logger.info(f"Insufficient data, attempting live ingestion for: {query}")
            
            ingestion_result = self.ingestor.ingest_query(
                query=query,
                domain=domain,
                use_live=True,
                max_fragments=self.max_fragments
            )
            
            if ingestion_result.fragments_created > 0:
                logger.info(f"Ingested {ingestion_result.fragments_created} new fragments")
                # Retry with fresh data
                response = self.answer(query, domain)
            
            response.metadata['ingestion'] = {
                'fragments_created': ingestion_result.fragments_created,
                'sources_processed': ingestion_result.sources_processed,
                'errors': ingestion_result.errors
            }
        
        return response
    
    def get_domain_stats(self, domain: str) -> Dict:
        """Get statistics for a specific domain."""
        try:
            fragments = self.retriever.get_fragments_by_domain(domain)
            
            if not fragments:
                return {
                    'domain': domain,
                    'fragment_count': 0,
                    'avg_confidence': 0.0,
                    'status': 'no_data'
                }
            
            avg_confidence = sum(f.get('confidence_score', 0.5) for f in fragments) / len(fragments)
            
            return {
                'domain': domain,
                'fragment_count': len(fragments),
                'avg_confidence': round(avg_confidence, 3),
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting domain stats: {e}")
            return {
                'domain': domain,
                'fragment_count': 0,
                'avg_confidence': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def clear_cache(self):
        """Clear cached data and reinitialize components."""
        self._retriever = None
        self._processor = None
        self._ingestor = None
        self._initialized = False
        logger.info("Pipeline cache cleared")


# Convenience function for backward compatibility
def create_pipeline() -> OpenEyesPipeline:
    """Create and return a pipeline instance."""
    return OpenEyesPipeline()
