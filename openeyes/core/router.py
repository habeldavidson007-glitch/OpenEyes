from __future__ import annotations

from openeyes.core.domain_validator import validate_query_domain

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
    "governance": (
        "government", "politics", "political", "legislative", "congress",
        "senate", "house", "parliament", "election", "voting", "democracy",
        "constitution", "law", "legal", "court", "judicial", "supreme court",
        "treaty", "international relations", "foreign policy", "diplomacy",
        "regulation", "policy", "federal", "state government", "local government",
        "executive", "president", "prime minister", "cabinet", "bureaucracy",
        "agency", "lobbying", "campaign", "party", "republican", "democrat",
        "filibuster", "veto", "impeachment", "redistricting", "gerrymandering",
        "sovereignty", "federalism", "separation of powers", "checks and balances",
        "civil rights", "constitutional law", "administrative law", "criminal law",
        "contract law", "tort law", "property law", "intellectual property",
        "patent", "copyright", "trademark", "national security", "defense",
        "military", "intelligence", "cybersecurity", "war", "conflict",
        "nato", "united nations", "security council", "genocide", "human rights"
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
    """
    P2 FIX: Use advanced domain validator with phrase/concept matching.
    
    If domain is explicitly provided, use it. Otherwise, use the advanced
    validator which provides better accuracy through context-aware matching.
    Falls back to keyword matching if validator returns unknown or low confidence.
    """
    if domain:
        return domain.lower()
    
    # Try advanced validator first
    validated_domain, confidence, _ = validate_query_domain(query)
    
    if validated_domain != "unknown" and confidence > 0.4:
        return validated_domain
    
    # Fallback to keyword matching
    q = query.lower()
    best = "general"
    best_score = 0

    for d, kws in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in q)
        if score > best_score:
            best = d
            best_score = score

    return best
