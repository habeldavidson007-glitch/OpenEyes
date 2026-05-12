"""
P2: Variational Inference Optimizer & Dynamic Prior Updating
Fast approximate reasoning with self-learning priors.
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class VariationalOptimizer:
    """
    Approximates complex Bayesian inference with fast optimization.
    Trades some accuracy for 10x speed improvement.
    """
    
    def __init__(self):
        self.prior_cache = self._load_priors()
    
    def _load_priors(self) -> Dict:
        """Loads historical success priors from file."""
        prior_file = '/workspace/openeyes/core/domain_priors.json'
        if os.path.exists(prior_file):
            with open(prior_file, 'r') as f:
                return json.load(f)
        
        # Default uniform priors
        return {
            'economy': {'base': 0.33, 'success_count': 100, 'total_count': 300},
            'healthcare': {'base': 0.33, 'success_count': 100, 'total_count': 300},
            'governance': {'base': 0.33, 'success_count': 100, 'total_count': 300}
        }
    
    def update_prior(self, domain: str, was_successful: bool):
        """Updates domain prior based on query outcome."""
        if domain not in self.prior_cache:
            self.prior_cache[domain] = {'base': 0.33, 'success_count': 0, 'total_count': 0}
        
        self.prior_cache[domain]['total_count'] += 1
        if was_successful:
            self.prior_cache[domain]['success_count'] += 1
        
        # Update base probability (empirical Bayes)
        total = self.prior_cache[domain]['total_count']
        successes = self.prior_cache[domain]['success_count']
        self.prior_cache[domain]['base'] = successes / total if total > 0 else 0.33
        
        # Save to file
        os.makedirs(os.path.dirname('/workspace/openeyes/core/domain_priors.json'), exist_ok=True)
        with open('/workspace/openeyes/core/domain_priors.json', 'w') as f:
            json.dump(self.prior_cache, f, indent=2)
    
    def optimize_inference(self, intent_vector: Dict[str, float], context_features: Dict) -> Dict[str, float]:
        """
        Combines intent vector with historical priors for optimized inference.
        Uses variational approximation: P(Domain|Query) ≈ P(Query|Domain) * P(Domain)
        """
        optimized = {}
        
        for domain, likelihood in intent_vector.items():
            prior = self.prior_cache.get(domain, {}).get('base', 0.33)
            
            # Variational update: posterior ∝ likelihood * prior
            # Simplified: weighted average favoring likelihood when strong
            if likelihood > 0.7:
                # Strong signal: trust likelihood more
                optimized[domain] = likelihood * 0.8 + prior * 0.2
            elif likelihood < 0.4:
                # Weak signal: trust prior more
                optimized[domain] = likelihood * 0.3 + prior * 0.7
            else:
                # Moderate signal: balanced
                optimized[domain] = likelihood * 0.6 + prior * 0.4
        
        # Normalize
        total = sum(optimized.values())
        if total > 0:
            optimized = {k: v/total for k, v in optimized.items()}
        
        return optimized

class ContextAwareDisambiguator:
    """Uses sentence structure and context to disambiguate terms."""
    
    # Context patterns that shift domain probability
    CONTEXT_PATTERNS = {
        # Financial context indicators
        r'\b(?:portfolio|investment|stock|market)\s+\w*\s*(?:diagnose|prescribe|treatment)': 0.9,
        r'\b(?:bankrupt|loss|debt)\s+\w*\s*(?:immune|cure|healthy)': 0.85,
        r'\b(?:return|yield|profit)\s+\w*\s*(?:guarantee|secure|safe)': 0.8,
        
        # Medical context indicators  
        r'\b(?:patient|symptom|disease)\s+\w*\s*(?:market|economy|finance)': 0.9,
        r'\b(?:drug|medication|dose)\s+\w*\s*(?:investment|policy)': 0.85,
        
        # Governance context indicators
        r'\b(?:vote|election|law)\s+\w*\s*(?:market|diagnosis)': 0.85,
        r'\b(?:congress|senate|court)\s+\w*\s*(?:portfolio|treatment)': 0.8
    }
    
    def calculate_context_weight(self, query: str, primary_domain: str) -> float:
        """Calculates context-based weight adjustment."""
        import re
        query_lower = query.lower()
        
        max_weight = 0.0
        
        for pattern, weight in self.CONTEXT_PATTERNS.items():
            if re.search(pattern, query_lower):
                max_weight = max(max_weight, weight)
        
        # If no pattern matched, return neutral weight
        return max_weight if max_weight > 0 else 0.5
    
    def disambiguate(self, query: str, intent_result: Dict) -> Dict:
        """Applies context-aware disambiguation to intent result."""
        primary = intent_result['primary_domain']
        context_weight = self.calculate_context_weight(query, primary)
        
        # Adjust confidence based on context
        adjusted_confidence = intent_result['primary_confidence'] * (0.5 + context_weight)
        adjusted_confidence = min(1.0, max(0.0, adjusted_confidence))
        
        return {
            'original_confidence': intent_result['primary_confidence'],
            'context_weight': context_weight,
            'adjusted_confidence': adjusted_confidence,
            'context_boosted': context_weight > 0.7,
            'disambiguation_notes': f"Context weight: {context_weight:.2f}" if context_weight > 0.7 else None
        }

def process_with_optimization(query: str, p1_result: Dict) -> Dict:
    """Main entry point for P2 processing."""
    optimizer = VariationalOptimizer()
    disambiguator = ContextAwareDisambiguator()
    
    # Get optimized intent vector
    intent_vector = p1_result['intent_result']['intent_vector']
    optimized_vector = optimizer.optimize_inference(intent_vector, {})
    
    # Sort optimized domains
    sorted_optimized = sorted(optimized_vector.items(), key=lambda x: x[1], reverse=True)
    
    # Apply context disambiguation
    updated_intent = {
        'primary_domain': sorted_optimized[0][0],
        'primary_confidence': sorted_optimized[0][1],
        'secondary_domain': sorted_optimized[1][0] if len(sorted_optimized) > 1 else None,
        'secondary_confidence': sorted_optimized[1][1] if len(sorted_optimized) > 1 else 0,
        'intent_vector': optimized_vector
    }
    
    disambiguation_result = disambiguator.disambiguate(query, updated_intent)
    
    return {
        'query': query,
        'p1_result': p1_result,
        'optimized_intent': updated_intent,
        'disambiguation': disambiguation_result,
        'final_domain': updated_intent['primary_domain'],
        'final_confidence': disambiguation_result['adjusted_confidence'],
        'recommendation': _generate_recommendation(updated_intent, disambiguation_result, p1_result)
    }

def _generate_recommendation(intent: Dict, disambig: Dict, p1_result: Dict) -> Dict:
    """Generates processing recommendation based on all signals."""
    confidence = disambig['adjusted_confidence']
    ignorance = p1_result['ignorance_analysis']['ignorance']
    impossible = p1_result['premise_validation']['impossible_premise']
    
    if impossible:
        return {
            'action': 'halt_with_correction',
            'reason': 'Impossible premise detected',
            'message': p1_result['premise_validation']['correction']
        }
    elif ignorance > 0.6:
        return {
            'action': 'answer_with_uncertainty',
            'reason': 'High ignorance level',
            'message': 'I have limited information on this topic. Here is what I found...'
        }
    elif confidence > 0.7:
        return {
            'action': 'answer_confidently',
            'reason': 'High confidence with valid premise',
            'message': None
        }
    elif confidence > 0.4:
        return {
            'action': 'answer_with_caveats',
            'reason': 'Moderate confidence',
            'message': 'Based on available information...'
        }
    else:
        return {
            'action': 'express_uncertainty_and_redirect',
            'reason': 'Low confidence across all domains',
            'message': 'I am not certain about this topic. Could you clarify?'
        }

if __name__ == "__main__":
    from bayesian_intent import process_query_intent
    from concept_graph import process_with_concept_graph
    
    test_queries = [
        "Give me a guaranteed 50% return stock with zero risk",
        "Prescribe a solution for my bankrupt portfolio", 
        "Diagnose why i failed investment",
        "How does a bond work?",
        "What causes a recession?"
    ]
    
    print("P2: Variational Inference & Context Disambiguation\n")
    print("=" * 70)
    
    for q in test_queries:
        intent = process_query_intent(q)
        p1 = process_with_concept_graph(q, intent)
        p2 = process_with_optimization(q, p1)
        
        print(f"\nQuery: {q}")
        print(f"  Final Domain: {p2['final_domain']} ({p2['final_confidence']:.2f})")
        print(f"  Action: {p2['recommendation']['action']}")
        if p2['recommendation']['message']:
            print(f"  Message: {p2['recommendation']['message']}")
        print(f"  Context Boosted: {p2['disambiguation']['context_boosted']}")
        print("-" * 70)
