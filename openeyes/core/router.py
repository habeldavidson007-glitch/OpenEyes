from __future__ import annotations

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "medical": ("symptom", "cancer", "diagnosis", "treatment", "drug", "disease", "patient", "hospital", "antibiotic", "medicine", "health"),
    "legal": ("law", "contract", "lawsuit", "legal", "rights", "court", "attorney", "judge"),
    "engineering": ("load", "beam", "concrete", "stress", "design", "safety factor", "structural"),
    "investment": ("investment", "stocks", "portfolio", "rich", "return", "risk", "finance", "money"),
    "cooking": ("recipe", "cook", "bake", "ingredients", "kitchen", "food"),
    "technology": ("quantum", "computer", "software", "algorithm", "AI", "machine learning", "tech", "blockchain", "crypto"),
    "science": ("physics", "chemistry", "biology", "experiment", "research", "scientific"),
}


def route_domain(query: str, domain: str | None = None) -> str:
    if domain:
        return domain.lower()
    q = query.lower()
    best = "general"
    best_score = 0
    for d, kws in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in q)
        if score > best_score:
            best = d
            best_score = score
    return best
