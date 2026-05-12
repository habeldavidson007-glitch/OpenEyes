from __future__ import annotations

# Three core domains with sector mappings
# ECO = Economy (fin, enr, com, mac, geo, reg sectors)
# GOV = Governance (leg, jud, sec, sub, ele, gel, gov, int, ipl sectors)
# HC = Healthcare (med, phr, mh, ph sectors)

CREDIBILITY_HIERARCHIES: dict[str, dict[str, int]] = {
    "economy": {
        "peer_reviewed_study": 95,
        "government_source": 90,
        "clinical_guideline": 88,
        "news_article": 65,
        "textbook": 80,
        "forum": 20,
        "sec_filing": 98,
        "regulatory_guidance": 95,
        "analyst_report": 70,
    },
    "governance": {
        "statute": 98,
        "case_law": 94,
        "government_source": 95,
        "peer_reviewed_study": 90,
        "secondary_source": 75,
        "news_article": 60,
        "forum": 20,
    },
    "healthcare": {
        "clinical_guideline": 98,
        "peer_reviewed_study": 95,
        "textbook": 85,
        "government_source": 92,
        "news_article": 55,
        "forum": 20,
    },
}

# Domain code normalization map - sectors map to their parent domains
DOMAIN_ALIASES: dict[str, str] = {
    # Healthcare sector codes
    "hc": "healthcare",
    "med": "healthcare",
    "phr": "healthcare",
    "mh": "healthcare",
    "ph": "healthcare",
    "medical": "healthcare",
    
    # Economy sector codes
    "eco": "economy",
    "fin": "economy",
    "enr": "economy",
    "com": "economy",
    "mac": "economy",
    "geo": "economy",
    "reg": "economy",
    "investment": "economy",
    "trading": "economy",
    "finance": "economy",
    
    # Governance sector codes
    "gov": "governance",
    "leg": "governance",
    "jud": "governance",
    "sec": "governance",
    "sub": "governance",
    "ele": "governance",
    "gel": "governance",
    "int": "governance",
    "ipl": "governance",
    "eng": "governance",  # Engineering falls under governance for regulations
    "legal": "governance",  # Legal falls under governance
}


def normalize_domain(domain: str) -> str:
    """Normalize domain code to canonical form (economy, governance, healthcare).
    
    All sector codes (fin, med, phr, leg, etc.) map to their parent domain.
    """
    if not domain:
        return "general"
    domain_lower = domain.lower()
    return DOMAIN_ALIASES.get(domain_lower, domain_lower)


def get_credibility_score(domain: str, source_type: str) -> int:
    """Get credibility score for a domain and source type."""
    normalized = normalize_domain(domain)
    return CREDIBILITY_HIERARCHIES.get(normalized, {}).get(source_type, 50)
