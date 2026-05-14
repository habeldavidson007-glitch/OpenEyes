"""
openeyes/pipeline/retriever.py

UnifiedRetriever: Consolidates all retrieval mechanisms into a single interface.
Replaces: retrieval.py, local_retrieval.py, live_fetch.py, fragment_orchestrator.py, graceful_degradation.py
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    fragments: List[Dict]
    source: str  # 'local', 'live', 'hybrid'
    confidence: float
    metadata: Dict

class UnifiedRetriever:
    """
    Unified retrieval interface that intelligently combines:
    - Local fragment retrieval
    - Live web fetching
    - Graceful degradation strategies
    
    Automatically selects the best retrieval strategy based on query type and available data.
    """
    
    def __init__(self):
        self.local_cache = {}
        self.live_enabled = os.getenv('OPENEYES_LIVE_FETCH', '1') == '1'
        self._initialize_components()
    
    def _initialize_components(self):
        """Lazy-load retrieval components only when needed."""
        self._local_retriever = None
        self._live_fetcher = None
        self._orchestrator = None
    
    @property
    def local_retriever(self):
        if self._local_retriever is None:
            from openeyes.knowledge.local_retrieval import LocalFragmentIndex, retrieve_local_fragments
            # Use the module functions directly instead of a class
            self._local_retriever = {
                'index_class': LocalFragmentIndex,
                'retrieve_func': retrieve_local_fragments
            }
        return self._local_retriever
    
    @property
    def live_fetcher(self):
        """Return the live_fetch module for backward compatibility.
        
        Note: This is a placeholder property. The actual live fetching
        is handled by the original retrieval.py implementation.
        New code should use openeyes.knowledge.live_fetch directly.
        """
        if self._live_fetcher is None and self.live_enabled:
            from openeyes.knowledge import live_fetch
            self._live_fetcher = live_fetch
        return self._live_fetcher
    
    def retrieve(self, query: str, domain: Optional[str] = None, 
                 max_results: int = 10, use_live: bool = True) -> RetrievalResult:
        """
        Main retrieval method with intelligent fallback.
        
        Strategy:
        1. Try local retrieval first (fastest)
        2. If insufficient results and live enabled, fetch from web
        3. Apply graceful degradation if needed
        4. Return unified result set
        """
        # Step 1: Local retrieval
        local_fragments = self._retrieve_local(query, domain, max_results)
        
        # Step 2: Check if we need live fetch
        if len(local_fragments) < 3 and use_live and self.live_fetcher:
            live_fragments = self._retrieve_live(query, domain, max_results - len(local_fragments))
            local_fragments.extend(live_fragments)
        
        # Step 3: Apply quality filtering and scoring
        filtered_fragments = self._filter_and_score(local_fragments, query)
        
        # Step 4: Determine source and confidence
        has_live = any(f.get('_source') == 'live' for f in filtered_fragments)
        has_local = any(f.get('_source') == 'local' for f in filtered_fragments)
        
        if has_live and has_local:
            source = 'hybrid'
        elif has_live:
            source = 'live'
        else:
            source = 'local'
        
        # Calculate overall confidence
        if filtered_fragments:
            avg_confidence = sum(f.get('confidence_score', 0.5) for f in filtered_fragments) / len(filtered_fragments)
        else:
            avg_confidence = 0.0
        
        return RetrievalResult(
            fragments=filtered_fragments[:max_results],
            source=source,
            confidence=avg_confidence,
            metadata={
                'total_found': len(filtered_fragments),
                'local_count': sum(1 for f in filtered_fragments if f.get('_source') == 'local'),
                'live_count': sum(1 for f in filtered_fragments if f.get('_source') == 'live'),
                'domain': domain
            }
        )
    
    def _retrieve_local(self, query: str, domain: Optional[str], max_results: int) -> List[Dict]:
        """Retrieve from local fragment storage."""
        try:
            # Use existing local retrieval module
            from openeyes.knowledge.retrieval import retrieve_records
            records = retrieve_records(query, domain=domain, limit=max_results * 2)
            
            fragments = []
            for record in records:
                if isinstance(record, dict):
                    record['_source'] = 'local'
                    fragments.append(record)
                else:
                    # Convert Fragment object to dict
                    frag_dict = {
                        'claim': getattr(record, 'content', '') or getattr(record, 'claim', ''),
                        'confidence_score': getattr(record, 'confidence_score', 0.5),
                        'source_url': getattr(record, 'source_url', ''),
                        'domain': getattr(record, 'domain', domain or ''),
                        '_source': 'local'
                    }
                    fragments.append(frag_dict)
            
            return fragments
        except Exception as e:
            logger.warning(f"Local retrieval failed: {e}")
            return []
    
    def _retrieve_live(self, query: str, domain: Optional[str], max_results: int) -> List[Dict]:
        """Fetch fresh fragments from web sources."""
        try:
            from openeyes.knowledge.live_fetch import fetch_live_fragments
            fragments = fetch_live_fragments(query, domain=domain, limit=max_results)
            
            for frag in fragments:
                frag['_source'] = 'live'
            
            return fragments
        except Exception as e:
            logger.warning(f"Live fetch failed: {e}")
            return []
    
    def _filter_and_score(self, fragments: List[Dict], query: str) -> List[Dict]:
        """Filter low-quality fragments and re-score based on query relevance."""
        if not fragments:
            return []
        
        query_lower = query.lower()
        query_words = set(w for w in query_lower.split() if len(w) > 2)
        
        scored_fragments = []
        for frag in fragments:
            content = frag.get('claim', '').lower()
            
            # Skip obvious junk
            if len(content) < 20:
                continue
            
            # Skip fragments with scraper artifacts
            if any(artifact in content for artifact in ['duckduckgo', 'search endpoint', 'retrieved 0']):
                continue
            
            # Boost score for query term matches
            content_words = set(content.split())
            overlap = query_words & content_words
            
            base_score = frag.get('confidence_score', 0.5)
            relevance_boost = min(0.3, len(overlap) * 0.1)
            new_score = min(1.0, base_score + relevance_boost)
            
            frag['confidence_score'] = new_score
            scored_fragments.append(frag)
        
        # Sort by confidence
        scored_fragments.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        return scored_fragments
    
    def get_fragments_by_domain(self, domain: str) -> List[Dict]:
        """Get all fragments for a specific domain."""
        try:
            from openeyes.fragment_library import FragmentLibrary
            lib = FragmentLibrary()
            fragments = lib.get_fragments_by_domain(domain)
            
            # Convert to dict format
            result = []
            for frag in fragments:
                if isinstance(frag, dict):
                    result.append(frag)
                else:
                    result.append({
                        'claim': getattr(frag, 'content', '') or getattr(frag, 'claim', ''),
                        'confidence_score': getattr(frag, 'confidence_score', 0.5),
                        'domain': getattr(frag, 'domain', domain)
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error getting fragments for domain {domain}: {e}")
            return []
