from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntentResult:
    """Result from intent routing with search strategy parameters."""
    intent_type: str       # factual_entity, current_events, theory, strategy
    search_mode: str       # BFS or DFS
    depth_limit: int       # How many DFS steps before stopping
    width_limit: int       # How many candidates per BFS pass


STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "for", "with", 
    "in", "on", "at", "to", "of", "and", "or", "but",
    "how", "which", "when", "where", "why", "can", "could",
    "should", "would", "may", "might", "must", "shall",
    "i", "me", "my", "we", "us", "our", "you", "your",
    "he", "she", "it", "they", "them", "their"
}


def route_intent(query: str, domain: str) -> IntentResult:
    q = query.lower()
    
    # Factual — BFS, wide and fast
    if q.startswith(("what is", "who is", "when did", "where is", "define", "explain")):
        return IntentResult("factual_entity", "BFS", depth_limit=1, width_limit=20)
    
    # Current events — BFS, prioritize recency
    if any(k in q for k in ["today", "current", "latest", "now", "recent", "2024", "2025"]):
        return IntentResult("current_events", "BFS", depth_limit=1, width_limit=15)
    
    # Theory — moderate DFS, follow causal chains
    if any(k in q for k in ["how", "why", "mechanism", "theory", "principle", "works"]):
        return IntentResult("theory", "DFS", depth_limit=3, width_limit=5)
    
    # Strategy — deep DFS, build reasoning chain step by step
    if any(k in q for k in ["best", "advice", "strategy", "should", "plan", "invest",
                              "recommend", "approach", "how to", "roadmap", "improve"]):
        return IntentResult("strategy", "DFS", depth_limit=5, width_limit=3)
    
    # Default — shallow DFS
    return IntentResult("theory", "DFS", depth_limit=2, width_limit=8)
