from __future__ import annotations


def route_intent(query: str, domain: str) -> str:
    q = query.lower()
    if q.startswith(("who is", "what is", "when did", "where is")):
        return "factual_entity"
    if any(k in q for k in ["today", "current", "latest", "news", "world", "global"]):
        return "current_events"
    if any(k in q for k in ["how", "why", "theory", "principle", "mechanism"]):
        return "theory"
    if any(k in q for k in ["plan", "strategy", "invest", "roadmap", "improve"]):
        return "strategy"
    return "theory"
