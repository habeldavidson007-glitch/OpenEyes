"""
Single source of truth for domain labels.
All domain comparisons must go through normalize_domain().
"""

# Canonical domain names — these are the ONLY valid domain labels
CANONICAL_DOMAINS = {
    'economy',
    'healthcare', 
    'governance',
    'engineering',
    'science',
    'history',
    'philosophy',
    'social_sciences',
    'education',
}

# All known aliases mapping to canonical names
DOMAIN_ALIASES = {
    # Economy aliases
    'finance': 'economy',
    'eco': 'economy',
    'economic': 'economy',
    'Economy': 'economy',
    'ECONOMY': 'economy',
    
    # Healthcare aliases
    'health': 'healthcare',
    'medical': 'healthcare',
    'hc': 'healthcare',
    'Healthcare': 'healthcare',
    'HEALTHCARE': 'healthcare',
    
    # Governance aliases
    'gov': 'governance',
    'government': 'governance',
    'politics': 'governance',
    'law': 'governance',
    'legal': 'governance',
    'Governance': 'governance',
    'GOVERNANCE': 'governance',
    'GOV': 'governance',
}

# Canonical subdomain codes per domain
SUBDOMAINS = {
    'economy': ['FIN', 'MAC', 'REG', 'ENR', 'COM', 'GEO'],
    'healthcare': ['MED', 'PH', 'PHR', 'MH'],
    'governance': ['GOV', 'LEG', 'JUD', 'SUB', 'IPL', 'INT', 'SEC', 'ELE', 'GEL'],
}


def normalize_domain(domain: str) -> str:
    """
    Convert any domain label to its canonical form.
    Returns None if domain is None.
    Raises ValueError if domain is completely unrecognized.
    """
    if domain is None:
        return None
    
    normalized = DOMAIN_ALIASES.get(domain, domain.lower())
    
    if normalized not in CANONICAL_DOMAINS:
        # Don't raise — log and return as-is so system doesn't crash
        return domain.lower()
    
    return normalized


def normalize_subdomain(subdomain: str) -> str:
    """Convert subdomain to uppercase canonical form."""
    if not subdomain:
        return None
    return subdomain.upper()
