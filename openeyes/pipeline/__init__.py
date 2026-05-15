"""
openeyes/pipeline/__init__.py

Unified Pipeline Architecture for OpenEyes.
Consolidates retrieval, processing, ingestion, and orchestration into streamlined modules.
"""

from .retriever import UnifiedRetriever
from .processor import QueryProcessor
from .ingestor import KnowledgeIngestor
from .orchestrator import OpenEyesPipeline

__all__ = [
    'UnifiedRetriever',
    'QueryProcessor', 
    'KnowledgeIngestor',
    'OpenEyesPipeline'
]
