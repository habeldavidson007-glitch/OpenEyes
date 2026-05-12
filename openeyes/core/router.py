from __future__ import annotations

from openeyes.knowledge.hierarchies import normalize_domain

# Three core domains only - all others are sectors within these domains
# ECO (Economy): fin, enr, com, mac, geo, reg sectors
# GOV (Governance): leg, jud, sec, sub, ele, gel, gov, int, ipl sectors  
# HC (Healthcare): med, phr, mh, ph sectors

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "economy": (
        "economy", "economic", "finance", "financial", "market", "trading",
        "investment", "stocks", "stock", "portfolio", "return", "risk", "money",
        "banking", "currency", "inflation", "gdp", "recession", "interest rate",
        "federal reserve", "fed", "crypto", "bitcoin", "ethereum", "bonds",
        "treasury", "earnings", "revenue", "valuation", "pe ratio", "dividend",
        "commodity", "oil", "gold", "energy", "geopolitical", "trade war",
        "tariff", "sanctions", "forex", "exchange rate", "hedge", "derivatives",
        "options", "futures", "etf", "index fund", "sector", "bull", "bear",
        "yield", "spread", "liquidity", "volatility", "short selling", "margin",
        "roi", "roe", "roa"
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
}


def route_domain(query: str, domain: str | None = None) -> str:
    """
    Route query to one of three core domains: economy, governance, healthcare.
    
    If domain is explicitly provided, normalize it. Otherwise, use keyword matching.
    All sector-specific queries (fin, leg, med, phr, etc.) route to their parent domain.
    """
    if domain:
        return normalize_domain(domain)
    
    # Keyword matching for three core domains
    q = query.lower()
    best = "general"
    best_score = 0

    for d, kws in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in q)
        if score > best_score:
            best = d
            best_score = score

    return normalize_domain(best)
