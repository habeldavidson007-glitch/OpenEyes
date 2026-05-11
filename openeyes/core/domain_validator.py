"""
P0 FIX: Domain Validation & Intent Pre-filtering
Routes queries to correct domain BEFORE retrieval to prevent cross-domain hallucination.
"""

import re
from typing import List, Tuple, Optional

DOMAIN_KEYWORDS = {
    'healthcare': [
        # Medical conditions
        'diabetes', 'hypertension', 'cancer', 'heart disease', 'stroke', 'asthma',
        'depression', 'anxiety', 'alzheimer', 'parkinson', 'arthritis', 'obesity',
        'migraine', 'epilepsy', 'hepatitis', 'hiv', 'aids', 'tuberculosis',
        # Symptoms
        'symptom', 'pain', 'fever', 'cough', 'nausea', 'vomiting', 'rash', 'swelling',
        'dizziness', 'fatigue', 'headache', 'shortness of breath', 'chest pain',
        # Treatments & Drugs
        'medication', 'drug', 'pills', 'dosage', 'side effects', 'prescription',
        'chemotherapy', 'radiation', 'surgery', 'vaccine', 'antibiotics',
        # Body systems
        'cardiovascular', 'respiratory', 'neurological', 'digestive', 'immune',
        'endocrine', 'renal', 'hepatic', 'pulmonary', 'metabolic',
        # Medical procedures
        'diagnosis', 'treatment', 'therapy', 'prognosis', 'clinical trial',
        'blood test', 'mri', 'ct scan', 'x-ray', 'biopsy'
    ],
    'economy': [
        # Macroeconomics
        'gdp', 'inflation', 'recession', 'unemployment', 'interest rate',
        'federal reserve', 'monetary policy', 'fiscal policy', 'quantitative easing',
        # Markets & Finance
        'stock market', 'bond', 'treasury', 'yield curve', 'forex', 'currency',
        'exchange rate', 'commodity', 'oil price', 'gold', 'cryptocurrency',
        # Banking
        'bank', 'lending', 'credit', 'mortgage', 'loan', 'debt', 'deficit',
        'financial crisis', 'bailout', 'liquidity', 'solvency',
        # Trade & Business
        'trade deficit', 'tariff', 'import', 'export', 'supply chain', 'manufacturing',
        'gdp growth', 'productivity', 'wage', 'income inequality', 'poverty rate',
        # Economic indicators
        'cpi', 'ppi', 'consumer confidence', 'retail sales', 'housing starts',
        'job report', 'nonfarm payroll'
    ],
    'governance': [
        # Government structure
        'congress', 'senate', 'house of representatives', 'parliament', 'legislature',
        'executive', 'judicial', 'supreme court', 'federalism', 'separation of powers',
        # Law & Legal
        'law', 'legislation', 'bill', 'act', 'statute', 'regulation', 'ordinance',
        'constitutional', 'amendment', 'jurisdiction', 'plaintiff', 'defendant',
        # Elections & Politics
        'election', 'vote', 'ballot', 'primary', 'caucus', 'electoral college',
        'gerrymandering', 'campaign finance', 'lobbying', 'political party',
        # International relations
        'treaty', 'diplomacy', 'foreign policy', 'nato', 'united nations', 'wto',
        'sanctions', 'embassy', 'ambassador', 'sovereignty',
        # Public policy
        'public policy', 'administrative', 'bureaucracy', 'agency', 'regulatory',
        'civil service', 'whistleblower', 'freedom of information'
    ],
    'engineering': [
        'engineer', 'design', 'prototype', 'manufacturing', 'cad', 'simulation',
        'structural', 'mechanical', 'electrical', 'chemical', 'civil', 'software',
        'algorithm', 'code', 'programming', 'api', 'database', 'cloud', 'devops'
    ]
}

# Domain-specific disambiguation rules
DISAMBIGUATION_RULES = {
    'bond': {
        'economy': ['treasury bond', 'corporate bond', 'municipal bond', 'bond yield', 'bond market'],
        'governance': ['bond measure', 'municipal bond election']
    },
    'security': {
        'economy': ['securities exchange', 'stock security', 'security analysis'],
        'governance': ['national security', 'security council', 'homeland security']
    },
    'treatment': {
        'healthcare': ['medical treatment', 'cancer treatment', 'drug treatment'],
        'governance': ['wastewater treatment', 'waste treatment regulation']
    }
}

def classify_domain(query: str) -> Tuple[str, float]:
    """
    Classify query into primary domain with confidence score.
    Returns (domain, confidence)
    """
    query_lower = query.lower()
    words = set(query_lower.split())
    
    domain_scores = {}
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in query_lower:
                # Multi-word keywords get higher weight
                word_count = len(keyword.split())
                score += word_count * 2
            # Also check individual words
            for word in words:
                if word == keyword or keyword.startswith(word):
                    score += 0.5
        
        domain_scores[domain] = score
    
    # Find best match
    best_domain = max(domain_scores, key=domain_scores.get)
    best_score = domain_scores[best_domain]
    
    # Calculate confidence
    total_score = sum(domain_scores.values())
    if total_score == 0:
        return 'unknown', 0.0
    
    confidence = best_score / max(total_score, 1)
    
    # Apply disambiguation rules
    for term, rules in DISAMBIGUATION_RULES.items():
        if term in query_lower:
            for rule_domain, phrases in rules.items():
                for phrase in phrases:
                    if phrase in query_lower:
                        if rule_domain == best_domain:
                            confidence = min(confidence + 0.2, 1.0)
                        break
    
    return best_domain, min(confidence, 1.0)

def get_allowed_domains(primary_domain: str, confidence: float) -> List[str]:
    """
    Determine which domains to search based on primary classification.
    High confidence = only primary domain
    Low confidence = primary + secondary domains
    """
    if confidence >= 0.7:
        return [primary_domain]
    elif confidence >= 0.4:
        # Add related domains
        related = {
            'healthcare': ['governance'],  # healthcare policy
            'economy': ['governance'],     # economic policy
            'governance': ['economy', 'healthcare'],
            'engineering': ['economy']
        }
        return [primary_domain] + related.get(primary_domain, [])
    else:
        # Very low confidence - search all but rank by relevance
        return ['healthcare', 'economy', 'governance', 'engineering']

def validate_domain_alignment(query: str, retrieved_fragments: List[dict]) -> bool:
    """
    Verify retrieved fragments match the query's intended domain.
    Returns False if significant misalignment detected.
    """
    if not retrieved_fragments:
        return True
    
    primary_domain, _ = classify_domain(query)
    
    if primary_domain == 'unknown':
        return True
    
    # Check if majority of fragments match expected domain
    matching_count = 0
    for fragment in retrieved_fragments[:5]:  # Check top 5
        frag_domain = fragment.get('domain', '').lower()
        if frag_domain == primary_domain or frag_domain in ['hc', 'healthcare'] and primary_domain == 'healthcare':
            matching_count += 1
        elif frag_domain in ['eco', 'economy'] and primary_domain == 'economy':
            matching_count += 1
        elif frag_domain in ['gov', 'governance'] and primary_domain == 'governance':
            matching_count += 1
    
    # Require at least 60% alignment
    return matching_count >= len(retrieved_fragments[:5]) * 0.6
