from __future__ import annotations

import re


def decompose_query(query: str) -> list[str]:
    q = query.strip().rstrip("?")
    # Extract key terms by removing common stop words and question phrases
    stop_words = {"tell", "me", "what", "is", "are", "the", "a", "an", "why", "how", "do", "does", "can", "could", "would", "should"}
    tokens = [t for t in q.lower().split() if t not in stop_words]
    
    # If we have meaningful keywords, use them; otherwise use the cleaned query
    if tokens:
        key_terms = " ".join(tokens[:5])  # Take top 5 keywords
    else:
        key_terms = q
    
    # Return the key terms for search
    return [key_terms] if key_terms else [q]
