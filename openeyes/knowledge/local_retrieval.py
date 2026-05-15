"""
P0 Implementation: Local Fragment Retrieval System (BACKWARD COMPATIBILITY WRAPPER)

This module is now a wrapper around the unified pipeline retriever.
All functionality has been migrated to openeyes/pipeline/retriever.py

For new code, use:
    from openeyes.pipeline.retriever import UnifiedRetriever
    retriever = UnifiedRetriever()
    results = retriever.retrieve(query, domain='healthcare')
"""

from openeyes.pipeline.retriever import UnifiedRetriever, LocalFragmentIndex, extract_keywords

# Create a singleton instance for backward compatibility
_unified_retriever = None

def _get_retriever():
    global _unified_retriever
    if _unified_retriever is None:
        _unified_retriever = UnifiedRetriever()
    return _unified_retriever


def retrieve_local_fragments(query: str, domain: str = None, limit: int = 10):
    """
    Backward-compatible function that delegates to UnifiedRetriever.
    
    Args:
        query: Search query string
        domain: Optional domain filter ('healthcare', 'economy', 'governance')
        limit: Maximum number of fragments to return
    
    Returns:
        List of fragment dictionaries
    """
    retriever = _get_retriever()
    result = retriever.retrieve(query, domain=domain, max_results=limit, use_live=False)
    return result.fragments


def search_local_index(query: str, domain: str = None, limit: int = 10):
    """
    Backward-compatible function for direct index search.
    
    Args:
        query: Search query string
        domain: Optional domain filter
        limit: Maximum number of results
    
    Returns:
        List of fragment dictionaries
    """
    retriever = _get_retriever()
    retriever.build_local_index()
    return retriever.local_index.search_by_keywords(query, domain=domain, limit=limit)


# Re-export LocalFragmentIndex for backward compatibility
__all__ = ['LocalFragmentIndex', 'retrieve_local_fragments', 'search_local_index', 'extract_keywords']
