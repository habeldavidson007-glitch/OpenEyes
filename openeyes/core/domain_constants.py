"""
Single source of truth for domain labels.
All domain comparisons must go through normalize_domain().

OpenEyes Master Domain Map — 8 Domains, 46 Sectors, ~8,900 Fragments
Architecture: Parent Domains → Sectors → Fragments
Fragment minimum per sector: 150
Three roles required per topic: definition, counter_argument, latest_data
"""

# Canonical domain names — these are the ONLY valid domain labels
CANONICAL_DOMAINS = {
    'economy',
    'healthcare', 
    'governance',
    'science_technology',
    'history',
    'philosophy_ethics',
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
    
    # Science & Technology aliases
    'science': 'science_technology',
    'technology': 'science_technology',
    'tech': 'science_technology',
    'sat': 'science_technology',
    'Science': 'science_technology',
    'TECH': 'science_technology',
    
    # History aliases
    'History': 'history',
    'HISTORY': 'history',
    'his': 'history',
    
    # Philosophy & Ethics aliases
    'philosophy': 'philosophy_ethics',
    'ethics': 'philosophy_ethics',
    'phi': 'philosophy_ethics',
    'Philosophy': 'philosophy_ethics',
    'PHI': 'philosophy_ethics',
    
    # Social Sciences aliases
    'social': 'social_sciences',
    'sociology': 'social_sciences',
    'psychology': 'social_sciences',
    'Social': 'social_sciences',
    'SOCIAL': 'social_sciences',
    
    # Education aliases
    'edu': 'education',
    'learning': 'education',
    'Education': 'education',
    'EDU': 'education',
}

# Canonical subdomain codes per domain with target fragment counts
# TIER 1 — ACTIVE (Building Now)
SUBDOMAINS = {
    # ECONOMY: How resources are produced, distributed, allocated, and governed financially.
    'economy': {
        'sectors': ['FIN', 'MAC', 'REG', 'ENR', 'COM', 'GEO'],
        'targets': {'FIN': 800, 'MAC': 300, 'REG': 150, 'ENR': 200, 'COM': 200, 'GEO': 200},
        'total': 1850,
        'sources': ['Federal Reserve', 'SEC', 'BLS', 'BEA', 'FRED', 'EIA', 'USDA', 'World Bank', 'IMF', 'WTO', 'OPEC']
    },
    # HEALTHCARE: How human health is understood, maintained, treated, and organized.
    'healthcare': {
        'sectors': ['MED', 'PH', 'PHR', 'MH'],
        'targets': {'MED': 400, 'PH': 250, 'PHR': 250, 'MH': 200},
        'total': 1100,
        'sources': ['PubMed', 'NICE', 'WHO', 'CDC', 'FDA', 'NIH', 'EMA', 'APA', 'Mayo Clinic']
    },
    # GOVERNANCE: How societies organize power, make collective decisions, codify rules.
    'governance': {
        'sectors': ['GOV', 'LEG', 'JUD', 'SUB', 'IPL', 'INT', 'SEC', 'ELE', 'GEL'],
        'targets': {'GOV': 200, 'LEG': 150, 'JUD': 150, 'SUB': 250, 'IPL': 100, 'INT': 200, 'SEC': 150, 'ELE': 100, 'GEL': 150},
        'total': 1450,
        'sources': ['Congress.gov', 'Federal Register', 'Supreme Court opinions', 'UN treaty database', 'ICJ decisions', 'CRS reports', 'WTO', 'CFR', 'Brookings', 'RAND', 'Freedom House', 'Inter-Parliamentary Union']
    },
    # SCIENCE & TECHNOLOGY: How the natural world works and how humans extend capabilities.
    'science_technology': {
        'sectors': ['PHY', 'BIO', 'ENV', 'CSC', 'SPC', 'ENG', 'MAT'],
        'targets': {'PHY': 200, 'BIO': 200, 'ENV': 200, 'CSC': 200, 'SPC': 150, 'ENG': 200, 'MAT': 150},
        'total': 1300,
        'sources': ['ArXiv', 'NASA', 'NIST', 'NSF', 'Nature', 'Science', 'IEEE', 'IPCC', 'NOAA', 'USGS']
    },
    # HISTORY: How human societies have developed, what events shaped them.
    'history': {
        'sectors': ['ANC', 'HMED', 'MOD', 'CON', 'REG', 'HIS'],  # HMED to avoid conflict with Healthcare MED
        'targets': {'ANC': 150, 'HMED': 150, 'MOD': 200, 'CON': 200, 'REG': 200, 'HIS': 100},
        'total': 1000,
        'sources': ['Academic history journals', 'University press publications', 'Library of Congress', 'National archives', 'Peer-reviewed historical research']
    },
    # PHILOSOPHY & ETHICS: Foundational questions of knowledge, value, reasoning, existence.
    'philosophy_ethics': {
        'sectors': ['ETH', 'LOG', 'PPH', 'MND', 'PHI'],
        'targets': {'ETH': 200, 'LOG': 150, 'PPH': 150, 'MND': 150, 'PHI': 150},
        'total': 800,
        'sources': ['Stanford Encyclopedia of Philosophy', 'Academic philosophy journals', 'Peer-reviewed publications']
    },
    # SOCIAL SCIENCES: How human behavior, societies, and institutions are studied empirically.
    'social_sciences': {
        'sectors': ['SOC', 'PSY', 'ANT', 'DEM', 'COM'],
        'targets': {'SOC': 200, 'PSY': 200, 'ANT': 150, 'DEM': 150, 'COM': 150},
        'total': 850,
        'sources': ['Academic social science journals', 'Pew Research Center', 'OECD', 'UN Population Division', 'American Sociological Review', 'Psychological Science']
    },
    # EDUCATION: How knowledge and skills are transmitted, developed, and evaluated.
    'education': {
        'sectors': ['LRN', 'EDU', 'HED', 'SKL'],
        'targets': {'LRN': 150, 'EDU': 150, 'HED': 150, 'SKL': 100},
        'total': 550,
        'sources': ['OECD PISA', 'Department of Education', 'ERIC database', 'American Educational Research Journal', 'Peer-reviewed education research']
    },
}

# Cross-domain relationships for automatic compatibility derivation
CROSS_DOMAIN_RELATIONSHIPS = [
    ('economy', 'GEO', 'governance', 'GEL', 'Geopolitical risk, sanctions, trade wars'),
    ('economy', 'REG', 'governance', 'LEG', 'Financial regulation as legislative product'),
    ('economy', 'MAC', 'governance', 'GOV', 'Fiscal policy, government spending'),
    ('economy', 'MAC', 'governance', 'LEG', 'Fiscal policy, government spending'),
    ('healthcare', 'PHR', 'governance', 'LEG', 'Drug regulation, FDA law, pricing legislation'),
    ('healthcare', 'PH', 'governance', 'SEC', 'Bioterrorism, pandemic preparedness, public health law'),
    ('science_technology', 'CSC', 'governance', 'SEC', 'Cybersecurity law, AI regulation'),
    ('science_technology', 'ENV', 'economy', 'ENR', 'Climate policy, energy transition'),
    ('science_technology', 'BIO', 'healthcare', 'MED', 'Genetics in clinical medicine, molecular diagnostics'),
    ('governance', 'GOV', 'philosophy_ethics', 'PPH', 'Political philosophy foundations of institutions'),
    ('governance', 'JUD', 'philosophy_ethics', 'ETH', 'Legal ethics, justice theory'),
    ('social_sciences', 'PSY', 'healthcare', 'MH', 'Clinical vs research psychology boundary'),
    ('history', 'CON', 'governance', 'INT', '20th century international relations as historical record'),
]

# Build sequence with phases
BUILD_SEQUENCE = [
    {'phase': 1, 'domain': 'economy', 'status': 'done', 'target': 1850},
    {'phase': 2, 'domain': 'healthcare', 'duration_weeks': 5, 'target': 1100},
    {'phase': 3, 'domain': 'governance', 'duration_weeks': 6, 'target': 1450},
    {'phase': 4, 'domain': 'science_technology', 'duration_weeks': 6, 'target': 1300},
    {'phase': 5, 'domain': 'history', 'duration_weeks': 8, 'target': 1000},
    {'phase': 6, 'domain': 'philosophy_ethics', 'duration_weeks': 6, 'target': 800},
    {'phase': 7, 'domain': 'social_sciences', 'duration_weeks': 6, 'target': 850},
    {'phase': 8, 'domain': 'education', 'duration_weeks': 4, 'target': 550},
]

# System totals
SYSTEM_TOTALS = {
    'tier1_active': {'domains': 2, 'sectors': 10, 'fragments': 2950},
    'tier2_next': {'domains': 2, 'sectors': 16, 'fragments': 2750},
    'tier3_longterm': {'domains': 4, 'sectors': 20, 'fragments': 3200},
    'full_system': {'domains': 8, 'sectors': 46, 'fragments': 8900},
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
