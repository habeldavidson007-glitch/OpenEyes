from __future__ import annotations

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "economy": (
        "economy", "economic", "finance", "financial", "market", "trading",
        "investment", "stocks", "portfolio", "return", "risk", "money",
        "banking", "currency", "inflation", "gdp", "recession", "interest rate",
        "federal reserve", "fed", "crypto", "bitcoin", "ethereum", "bonds",
        "treasury", "earnings", "revenue", "valuation", "pe ratio", "dividend",
        "commodity", "oil", "gold", "energy", "geopolitical", "trade war",
        "tariff", "sanctions", "forex", "exchange rate", "hedge", "derivatives",
        "options", "futures", "etf", "index fund", "sector", "bull", "bear",
        "yield", "spread", "liquidity", "volatility", "short selling", "margin"
    ),
    "healthcare": (
        "health", "medical", "medicine", "doctor", "patient", "disease",
        "symptom", "diagnosis", "treatment", "drug", "vaccine", "cancer",
        "surgery", "hospital", "clinical", "pharmaceutical", "therapy",
        "antibiotic", "virus", "bacteria", "chronic", "acute", "mental health",
        "nutrition", "exercise", "wellness", "public health", "epidemiology",
        "mrna", "immune", "antibody", "dose", "trial", "fda", "who", "nih"
    ),
    "engineering": (
        "load", "beam", "concrete", "stress", "design", "safety factor",
        "structural", "civil", "mechanical", "electrical", "circuit", "voltage",
        "material", "tensile", "compression", "welding", "blueprint"
    ),
    "legal": (
        "law", "contract", "lawsuit", "legal", "rights", "court",
        "attorney", "judge", "regulation", "compliance", "statute",
        "precedent", "liability", "tort", "jurisdiction"
    ),
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
