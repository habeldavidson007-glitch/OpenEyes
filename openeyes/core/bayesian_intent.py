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
        r"\bdiagnose\b.*(?:investment|portfolio|stock|market|fund|asset)": "analyze investment performance",
        r"\bprescribe\b.*(?:solution|fix|remedy).*(?:portfolio|loss|debt|fund)": "recommend financial strategy",
        r"\bimmune\b.*(?:failure|loss|risk)": "mitigate risk",
        r"\bsymptoms\b.*(?:recession|inflation|crash)": "indicators of economic downturn",
        r"\btreatment\b.*(?:debt|bankruptcy|loss)": "debt management plan",
        r"\bhealthy\b.*(?:portfolio|economy|fund)": "stable financial position",
        r"\bsurgery\b.*(?:portfolio|investment|fund)": "major portfolio restructuring",
        r"\boperation\b.*(?:financial|investment)": "financial maneuver",
        
        # Legal/Governance -> Economic
        r"\bvote\b.*(?:investment|choice|selection|portfolio|stock)": "decision making criteria",
        r"\bverdict\b.*(?:market|stock|investment|portfolio)": "market analysis conclusion",
        r"\bliable\b.*(?:loss|debt|investment)": "financial responsibility",
        r"\btrial\b.*(?:investment|portfolio)": "investment evaluation",
        r"\bjudge\b.*(?:investment|stock|portfolio)": "evaluate investment",
        r"\bcourt\b.*(?:opinion|view).*(?:market|investment)": "market perspective",
        
        # General Metaphors
        r"\bbleeding\b.*(?:money|capital|cash|fund)": "sustained financial losses",
        r"\bdrowning\b.*(?:debt|loans|obligations)": "overwhelmed by debt obligations",
        r"\bsuffocating\b.*(?:regulation|taxes|costs)": "burdened by regulatory costs",
        r"\bsinking\b.*(?:investment|portfolio|fund)": "failing investment",
        r"\bcrash\b.*(?:investment|portfolio)": "investment collapse",
    }

    # Domain override words that should NOT trigger wrong domain when in financial context
    DOMAIN_OVERRIDE_CONTEXT = {
        'vote': ['investment', 'portfolio', 'stock', 'fund', 'choice', 'selection'],
        'verdict': ['market', 'stock', 'investment', 'portfolio', 'trade'],
        'surgery': ['portfolio', 'investment', 'fund', 'financial', 'balance', 'sheet', 'company', 'business', 'corporate'],
        'diagnosis': ['investment', 'portfolio', 'market', 'economic'],
        'treatment': ['portfolio', 'debt', 'investment', 'financial'],
        'prescribe': ['portfolio', 'investment', 'strategy', 'fund'],
        'symptoms': ['recession', 'inflation', 'market', 'economic'],
        'immune': ['portfolio', 'investment', 'risk', 'loss', 'financial'],
    }

    def rewrite_query(self, query: str) -> Tuple[str, bool]:
        """
        Rewrites metaphorical queries to literal domain terms.
        Returns (rewritten_query, is_metaphorical)
        """
        original = query.lower()
        rewritten = original
        is_metaphorical = False
        
        # Check if metaphor word appears with domain context
        for metaphor_word, context_words in self.DOMAIN_OVERRIDE_CONTEXT.items():
            if metaphor_word in original:
                # If any context word is present, it's likely a financial metaphor
                if any(ctx in original for ctx in context_words):
                    is_metaphorical = True
                    break
        
        # Special case: "surgery on" with financial context should be marked metaphorical
        if 'surgery' in original and any(word in original for word in ['balance', 'sheet', 'company', 'business', 'portfolio']):
            is_metaphorical = True
            rewritten = re.sub(r'\bsurgery\b', 'major restructuring', original)
        
        # Apply pattern-based rewrites
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
            'bankrupt', 'debt', 'loan', 'mortgage', 'credit', 'finance',
            'fund', 'funds', 'trading', 'broker', 'hedge', 'derivative'
        ],
        'healthcare': [
            'diagnosis', 'treatment', 'symptom', 'medication', 'drug', 'dose', 
            'patient', 'hospital', 'doctor', 'nurse', 'disease', 'condition',
            'therapy', 'surgery', 'cancer', 'heart', 'lung', 'virus', 'bacteria',
            'mental health', 'depression', 'anxiety', 'suicide', 'overdose',
            'pills', 'prescription', 'overdose', 'self-harm', 'hurt myself'
        ],
        'governance': [
            'law', 'bill', 'act', 'congress', 'senate', 'vote', 'election', 
            'president', 'court', 'judge', 'constitution', 'amendment', 'treaty',
            'regulation', 'policy', 'agency', 'department', 'sovereignty',
            'democracy', 'authoritarian', 'rights', 'legislation', 'government'
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
        'vote': {'governance': 0.7, 'economy': 0.2, 'healthcare': 0.1},
        'surgery': {'healthcare': 0.8, 'economy': 0.15, 'governance': 0.05},
        'diagnose': {'healthcare': 0.7, 'economy': 0.25, 'governance': 0.05},
        'prescribe': {'healthcare': 0.7, 'economy': 0.25, 'governance': 0.05},
    }
    
    # Context boosters: if these words appear, boost economy domain for ambiguous terms
    FINANCIAL_CONTEXT_BOOSTERS = [
        'investment', 'portfolio', 'stock', 'fund', 'market', 'money', 'capital',
        'asset', 'return', 'profit', 'loss', 'debt', 'bankrupt', 'financial',
        'trading', 'broker', 'hedge', 'equity', 'bond', 'yield', 'dividend',
        'crypto', 'savings', 'mortgage', 'loans', 'balance', 'sheet', 'company',
        'business', 'corporate'
    ]
    
    MEDICAL_CONTEXT_BOOSTERS = [
        'patient', 'doctor', 'hospital', 'pills', 'medication', 'health',
        'disease', 'symptom', 'treatment', 'diagnosis', 'therapy', 'medical',
        'chest', 'pain', 'overdose', 'hurt', 'self-harm', 'die', 'suicide'
    ]
    
    GOVERNANCE_CONTEXT_BOOSTERS = [
        'law', 'congress', 'senate', 'government', 'policy', 'regulation',
        'election', 'vote', 'legislation', 'court', 'legal', 'politician',
        'country', 'democracy', 'power', 'authority'
    ]

    def calculate_vector(self, query: str) -> Dict[str, float]:
        """Returns probability distribution across domains."""
        tokens = set(re.findall(r'\b\w+\b', query.lower()))
        scores = {'economy': 0.0, 'healthcare': 0.0, 'governance': 0.0}
        total_weight = 0.0
        
        # Detect context first - check for multi-word phrases too
        query_lower = query.lower()
        has_financial_context = any(token in self.FINANCIAL_CONTEXT_BOOSTERS for token in tokens)
        has_medical_context = any(token in self.MEDICAL_CONTEXT_BOOSTERS for token in tokens) or 'chest pain' in query_lower or 'self harm' in query_lower
        has_governance_context = any(token in self.GOVERNANCE_CONTEXT_BOOSTERS for token in tokens)
        
        # Special handling for self-harm queries - always route to healthcare
        self_harm_phrases = ['end it', 'want to die', 'hurt myself', 'hurting myself', 
                            'drive off a bridge', 'stop breathing', 'peaceful way to exit',
                            'take all my pills', 'overdose', 'kill myself']
        if any(phrase in query_lower for phrase in self_harm_phrases):
            return {'economy': 0.05, 'healthcare': 0.90, 'governance': 0.05}
        
        # Also check for "bridge" with self-harm context
        if 'bridge' in tokens and any(word in tokens for word in ['car', 'drive', 'off']):
            return {'economy': 0.05, 'healthcare': 0.90, 'governance': 0.05}
        
        # Special handling for "chest pain" - always healthcare
        if 'chest' in tokens and 'pain' in tokens:
            return {'economy': 0.10, 'healthcare': 0.85, 'governance': 0.05}
        
        # Special handling for "cure all diseases" - detect as impossible premise (will be caught by P1)
        # But route to healthcare domain first since it's a medical query
        if 'cure' in tokens and ('disease' in tokens or 'diseases' in tokens) and 'all' in tokens:
            return {'economy': 0.05, 'healthcare': 0.90, 'governance': 0.05}
        
        # Special handling for "surgery on company/balance sheet" - financial metaphor
        if 'surgery' in tokens and any(word in tokens for word in ['company', 'balance', 'sheet', 'portfolio', 'business']):
            return {'economy': 0.85, 'healthcare': 0.10, 'governance': 0.05}
        
        for token in tokens:
            if token in self.AMBIGUOUS_WORDS:
                # Adjust weights based on context
                base_weights = self.AMBIGUOUS_WORDS[token].copy()
                
                # Apply context boosts
                if has_financial_context and token in ['vote', 'surgery', 'diagnose', 'prescribe', 'verdict']:
                    base_weights['economy'] = base_weights.get('economy', 0) + 0.4
                if has_medical_context and token == 'bond':
                    base_weights['healthcare'] = base_weights.get('healthcare', 0) + 0.3
                if has_governance_context and token == 'fund':
                    base_weights['governance'] = base_weights.get('governance', 0) + 0.3
                
                for domain, weight in base_weights.items():
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
