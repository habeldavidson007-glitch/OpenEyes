from __future__ import annotations

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "medical": ("symptom", "cancer", "diagnosis", "treatment", "drug", "disease"),
    "legal": ("law", "contract", "lawsuit", "legal", "rights", "court"),
    "engineering": ("load", "beam", "concrete", "stress", "design", "safety factor"),
    "investment": ("investment", "stocks", "portfolio", "rich", "return", "risk"),
    "cooking": ("recipe", "cook", "bake", "ingredients", "kitchen"),
}


def route_domain(query: str, domain: str | None = None) -> str:
    if domain:
        return domain.lower()
    q = query.lower()
    best = "medical"
    best_score = -1
    for d, kws in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in q)
        if score > best_score:
            best = d
            best_score = score
    return best
