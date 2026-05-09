"""
OpenEyes Consistency Checker: Binary Search Verification

This module provides O(log n) consistency verification for new fragments
against the existing binary library. It uses keyword indexing and binary
search to quickly detect contradictions.
"""

from __future__ import annotations

from typing import List, Dict, Any
from openeyes.knowledge.fragments import Fragment


def verify_consistency(
    new_fragments: List[Fragment],
    existing_fragments: List[Fragment],
    tolerance: float = 0.3
) -> List[Fragment]:
    """
    Verify new fragments are consistent with existing knowledge using Binary Search.
    
    This is a re-export of the function from auto_fragment.py for cleaner imports.
    See auto_fragment.py for full implementation.
    """
    from .auto_fragment import verify_consistency as _verify
    
    return _verify(new_fragments, existing_fragments, tolerance)


def build_binary_search_index(fragments: List[Fragment]) -> Dict[str, List[Fragment]]:
    """
    Build a binary-searchable index of fragments by keywords.
    
    Enables O(log n) lookup instead of O(n) linear search.
    """
    from .auto_fragment import _build_keyword_index
    return _build_keyword_index(fragments)


if __name__ == "__main__":
    print("Consistency Checker module loaded successfully")
    print("Use verify_consistency() to check new fragments against existing knowledge")
