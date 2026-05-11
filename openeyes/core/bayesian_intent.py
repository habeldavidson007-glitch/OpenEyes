"""
P0: Semantic De-Metaphorization & Intent Vector Engine
Replaces binary keyword matching with probabilistic intent inference.
"""

import re
from typing import Dict, List, Tuple

class SemanticRewriter:
    """Translates metaphors into domain-specific concepts."""
    
    METAPHOR_MAP = {
        # Medical -> Economic
        r"\bdiagnose\b.*(?:investment|portfolio|stock|market)": "analyze investment performance",
        r"\bprescribe\b.*(?:solution|fix|remedy).*(?:portfolio|loss|debt)": "recommend financial strategy",
        r"\bimmune\b.*(?:failure|loss|risk)": "mitigate risk",
        r"\bsymptoms\b.*(?:recession|inflation|crash)": "indicators of economic downturn",
        r"\btreatment\b.*(?:debt|bankruptcy)": "debt management plan",
        r"\bhealthy\b.*(?:portfolio|economy)": "stable financial position",
        
        # Legal -> Economic
        r"\bvote\b.*(?:investment|choice|selection)": "decision making criteria",
        r"\bverdict\b.*(?:market|stock)": "market analysis conclusion",
        r"\bliable\b.*(?:loss|debt)": "financial responsibility",
        
        # General Metaphors
        r"\bbleeding\b.*(?:money|capital|cash)": "sustained financial losses",
        r"\bdrowning\b.*(?:debt|loans)": "overwhelmed by debt obligations",
        r"\bsuffocating\b.*(?:regulation|taxes)": "burdened by regulatory costs",
    }

    def rewrite_query(self, query: str) -> Tuple[str, bool]:
        """
        Rewrites metaphorical queries to literal domain terms.
        Returns (rewritten_query, is_metaphorical)
        """
        original = query.lower()
        rewritten = original
        is_metaphorical = False
        
        for pattern, replacement in self.METAPHOR_MAP.items():
            if re.search(pattern, original):
                rewritten = re.sub(pattern, replacement, original)
                is_metaphorical = True
                break  # Apply one primary rewrite to avoid over-correction
        
        return rewritten, is_metaphorical

class IntentVectorCalculator:
    """Calculates P(Domain|Query) probability distribution."""
    
    DOMAIN_SIGNALS = {
        'economy': [
            'investment', 'portfolio', 'stock', 'bond', 'market', 'federal funds', 
            'inflation', 'recession', 'gdp', 'interest rate', 'crypto', 'asset', 
            'return', 'yield', 'dividend', 'equity', 'capital', 'liquidity',
            'bankrupt', 'debt', 'loan', 'mortgage', 'credit', 'finance'
        ],
        'healthcare': [
            'diagnosis', 'treatment', 'symptom', 'medication', 'drug', 'dose', 
            'patient', 'hospital', 'doctor', 'nurse', 'disease', 'condition',
            'therapy', 'surgery', 'cancer', 'heart', 'lung', 'virus', 'bacteria',
            'mental health', 'depression', 'anxiety', 'suicide', 'overdose'
        ],
        'governance': [
            'law', 'bill', 'act', 'congress', 'senate', 'vote', 'election', 
            'president', 'court', 'judge', 'constitution', 'amendment', 'treaty',
            'regulation', 'policy', 'agency', 'department', 'sovereignty',
            'democracy', 'authoritarian', 'rights', 'legislation'
        ]
    }
    
    # Words that appear in multiple domains (need context weighting)
    AMBIGUOUS_WORDS = {
        'bond': {'economy': 0.8, 'governance': 0.2},  # Financial bond vs Social bond
        'rate': {'economy': 0.9, 'healthcare': 0.1},  # Interest rate vs Heart rate
        'power': {'governance': 0.6, 'economy': 0.2, 'healthcare': 0.2},
        'work': {'economy': 0.4, 'healthcare': 0.3, 'governance': 0.3},
        'cause': {'healthcare': 0.5, 'economy': 0.3, 'governance': 0.2},
        'secure': {'economy': 0.5, 'governance': 0.4, 'healthcare': 0.1},
        'fund': {'economy': 0.9, 'governance': 0.1},
        'trust': {'economy': 0.6, 'governance': 0.2, 'healthcare': 0.2},
        'treatment': {'healthcare': 0.7, 'economy': 0.2, 'governance': 0.1},
        'failure': {'economy': 0.5, 'healthcare': 0.3, 'governance': 0.2},
        'verdict': {'governance': 0.6, 'economy': 0.3, 'healthcare': 0.1},
        'liability': {'governance': 0.5, 'economy': 0.4, 'healthcare': 0.1},
        'structure': {'governance': 0.4, 'economy': 0.3, 'healthcare': 0.3},
        'diabetes': {'healthcare': 1.0},
        'vaccines': {'healthcare': 1.0},
        'mRNA': {'healthcare': 1.0},
        'hypertension': {'healthcare': 1.0},
        'symptoms': {'healthcare': 0.8, 'economy': 0.2},
    }

    def calculate_vector(self, query: str) -> Dict[str, float]:
        """Returns probability distribution across domains."""
        tokens = set(re.findall(r'\b\w+\b', query.lower()))
        scores = {'economy': 0.0, 'healthcare': 0.0, 'governance': 0.0}
        total_weight = 0.0
        
        for token in tokens:
            if token in self.AMBIGUOUS_WORDS:
                # Use pre-defined weights for ambiguous words
                for domain, weight in self.AMBIGUOUS_WORDS[token].items():
                    scores[domain] += weight
                    total_weight += weight
            else:
                # Check direct signals
                for domain, signals in self.DOMAIN_SIGNALS.items():
                    if token in signals:
                        scores[domain] += 1.0
                        total_weight += 1.0
        
        # Normalize to probabilities
        if total_weight == 0:
            return {'economy': 0.33, 'healthcare': 0.33, 'governance': 0.34}
        
        return {d: s / total_weight for d, s in scores.items()}

def process_query_intent(query: str) -> Dict:
    """Main entry point for P0 processing."""
    rewriter = SemanticRewriter()
    calculator = IntentVectorCalculator()
    
    # Step 1: Rewrite metaphors
    rewritten_query, is_metaphorical = rewriter.rewrite_query(query)
    
    # Step 2: Calculate intent vector on BOTH original and rewritten
    original_vector = calculator.calculate_vector(query)
    rewritten_vector = calculator.calculate_vector(rewritten_query)
    
    # Blend vectors if metaphorical (trust rewritten more)
    if is_metaphorical:
        final_vector = {
            k: (original_vector[k] * 0.3 + rewritten_vector[k] * 0.7)
            for k in original_vector
        }
    else:
        final_vector = original_vector
    
    # Sort by probability
    sorted_domains = sorted(final_vector.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'original_query': query,
        'rewritten_query': rewritten_query,
        'is_metaphorical': is_metaphorical,
        'intent_vector': final_vector,
        'primary_domain': sorted_domains[0][0],
        'primary_confidence': sorted_domains[0][1],
        'secondary_domain': sorted_domains[1][0] if len(sorted_domains) > 1 else None,
        'secondary_confidence': sorted_domains[1][1] if len(sorted_domains) > 1 else 0
    }

if __name__ == "__main__":
    # Test cases
    test_queries = [
        "Diagnose why i failed investment",
        "Prescribe a solution for my bankrupt portfolio",
        "What is the federal funds rate?",
        "How does a bond work?",
        "I think I overdosed on pills"
    ]
    
    for q in test_queries:
        result = process_query_intent(q)
        print(f"Query: {q}")
        print(f"  Rewritten: {result['rewritten_query']}")
        print(f"  Metaphorical: {result['is_metaphorical']}")
        print(f"  Primary Domain: {result['primary_domain']} ({result['primary_confidence']:.2f})")
        print(f"  Secondary Domain: {result['secondary_domain']} ({result['secondary_confidence']:.2f})")
        print("-" * 40)
