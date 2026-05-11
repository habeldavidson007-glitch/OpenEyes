"""
P1: Concept Graph & Ignorance Handling
Implements cross-domain concept linking and Dempster-Shafer ignorance metric.
"""

from typing import Dict, List, Set, Tuple

class ConceptGraph:
    """Links related concepts across domains logically."""
    
    # Cross-domain concept mappings
    CONCEPT_LINKS = {
        'risk': {
            'economy': ['volatility', 'diversification', 'hedge', 'insurance'],
            'healthcare': ['pathogen', 'complication', 'side_effect', 'contraindication'],
            'governance': ['threat', 'security', 'liability', 'regulation']
        },
        'failure': {
            'economy': ['bankruptcy', 'default', 'loss', 'insolvency'],
            'healthcare': ['mortality', 'complication', 'adverse_event'],
            'governance': ['policy_failure', 'institutional_collapse']
        },
        'immune': {
            'economy': ['hedged', 'insured', 'diversified', 'protected'],
            'healthcare': ['antibody', 'vaccination', 'resistance'],
            'governance': ['sovereign_immunity', 'diplomatic_immunity']
        },
        'diagnosis': {
            'economy': ['analysis', 'assessment', 'audit', 'evaluation'],
            'healthcare': ['diagnosis', 'screening', 'test_result'],
            'governance': ['investigation', 'inquiry', 'oversight']
        },
        'treatment': {
            'economy': ['remedy', 'solution', 'strategy', 'intervention'],
            'healthcare': ['therapy', 'medication', 'surgery'],
            'governance': ['policy_response', 'legislative_action']
        }
    }
    
    def get_related_concepts(self, concept: str, target_domain: str) -> List[str]:
        """Returns domain-specific related concepts for a given term."""
        if concept in self.CONCEPT_LINKS:
            return self.CONCEPT_LINKS[concept].get(target_domain, [])
        return []
    
    def find_cross_domain_bridge(self, concept: str, source_domain: str, target_domain: str) -> Tuple[str, str]:
        """
        Finds conceptual bridge between domains.
        Returns (source_concept, target_concept) or (None, None) if no bridge.
        """
        if concept in self.CONCEPT_LINKS:
            source_concepts = self.CONCEPT_LINKS[concept].get(source_domain, [])
            target_concepts = self.CONCEPT_LINKS[concept].get(target_domain, [])
            
            if source_concepts and target_concepts:
                return (source_concepts[0], target_concepts[0])
        
        return (None, None)

class IgnoranceCalculator:
    """
    Implements Dempster-Shafer theory to distinguish between
    uncertainty (low confidence) and ignorance (unknown unknowns).
    """
    
    def calculate_ignorance(self, intent_vector: Dict[str, float]) -> Dict[str, float]:
        """
        Calculates belief, disbelief, and ignorance masses.
        
        Returns:
        - belief: Evidence supporting the primary domain
        - disbelief: Evidence against the primary domain
        - ignorance: Lack of evidence (unknown)
        """
        if not intent_vector:
            return {'belief': 0.0, 'disbelief': 0.0, 'ignorance': 1.0}
        
        # Sort domains by probability
        sorted_domains = sorted(intent_vector.items(), key=lambda x: x[1], reverse=True)
        primary_confidence = sorted_domains[0][1]
        secondary_confidence = sorted_domains[1][1] if len(sorted_domains) > 1 else 0.0
        
        # Dempster-Shafer masses
        belief = primary_confidence  # Evidence for primary domain
        disbelief = 1.0 - primary_confidence  # Evidence against (sum of others)
        
        # Ignorance: gap between belief + disbelief and 1.0
        # High ignorance when all probabilities are low/uniform
        if len(sorted_domains) == 3:
            uniformity = 1.0 - (primary_confidence - 0.33) * 3  # Deviation from uniform
            ignorance = max(0.0, min(1.0, uniformity * (1.0 - primary_confidence)))
        else:
            ignorance = 1.0 - primary_confidence
        
        return {
            'belief': belief,
            'disbelief': disbelief,
            'ignorance': ignorance,
            'is_ignorant': ignorance > 0.6  # Threshold for "we don't know enough"
        }

class PremiseValidator:
    """Detects logically impossible or contradictory premises."""
    
    IMPOSSIBLE_PATTERNS = [
        # Financial impossibilities
        (r'\bguaranteed\b.*\breturn\b.*\bzero\s+risk\b', "No investment guarantees returns with zero risk"),
        (r'\bimmune\b.*\b(?:failure|loss|risk)\b', "No strategy provides complete immunity to financial loss"),
        (r'\b100%\s*(?:success|profit|gain)\b', "No investment has 100% success rate"),
        (r'\bfree\s+money\b', "There is no such thing as free money without risk or effort"),
        
        # Medical impossibilities
        (r'\bcure\s+all\b.*\bdisease\b', "No single cure exists for all diseases"),
        (r'\bzero\s+side\s+effects\b', "All medical interventions carry some risk of side effects"),
        
        # Governance impossibilities
        (r'\bperfect\s+democracy\b', "No political system achieves perfect democracy"),
        (r'\babsolute\s+power\b.*\bno\s+corruption\b', "Absolute power without corruption is historically unprecedented"),
    ]
    
    def validate_premise(self, query: str) -> Dict:
        """
        Checks if query contains impossible premises.
        Returns validation result with correction suggestion.
        """
        import re
        
        query_lower = query.lower()
        
        for pattern, correction in self.IMPOSSIBLE_PATTERNS:
            if re.search(pattern, query_lower):
                return {
                    'is_valid': False,
                    'impossible_premise': True,
                    'correction': correction,
                    'suggested_reframe': f"While {correction.lower()}, I can explain risk management strategies..."
                }
        
        return {
            'is_valid': True,
            'impossible_premise': False,
            'correction': None,
            'suggested_reframe': None
        }

def process_with_concept_graph(query: str, intent_result: Dict) -> Dict:
    """Main entry point for P1 processing."""
    graph = ConceptGraph()
    ignorance_calc = IgnoranceCalculator()
    premise_validator = PremiseValidator()
    
    # Get concept bridges for top 2 domains
    primary = intent_result['primary_domain']
    secondary = intent_result['secondary_domain']
    
    # Extract key concepts from query (simplified)
    key_concepts = ['risk', 'failure', 'immune']  # Would be NLP-extracted in production
    
    bridges = {}
    for concept in key_concepts:
        if secondary:
            bridge = graph.find_cross_domain_bridge(concept, secondary, primary)
            if bridge[0]:
                bridges[concept] = bridge
    
    # Calculate ignorance
    ignorance_result = ignorance_calc.calculate_ignorance(intent_result['intent_vector'])
    
    # Validate premise
    premise_result = premise_validator.validate_premise(query)
    
    return {
        'query': query,
        'intent_result': intent_result,
        'concept_bridges': bridges,
        'ignorance_analysis': ignorance_result,
        'premise_validation': premise_result,
        'should_halt_for_impossibility': not premise_result['is_valid'] and premise_result['impossible_premise'],
        'should_express_uncertainty': ignorance_result['is_ignorant']
    }

if __name__ == "__main__":
    from bayesian_intent import process_query_intent
    
    test_queries = [
        "Give me a guaranteed 50% return stock with zero risk",
        "Prescribe a solution for my bankrupt portfolio",
        "How does a bond work?",
        "What causes a recession?"
    ]
    
    for q in test_queries:
        intent = process_query_intent(q)
        result = process_with_concept_graph(q, intent)
        
        print(f"Query: {q}")
        print(f"  Primary Domain: {result['intent_result']['primary_domain']}")
        print(f"  Ignorance: {result['ignorance_analysis']['ignorance']:.2f} (Ignorant: {result['ignorance_analysis']['is_ignorant']})")
        print(f"  Valid Premise: {result['premise_validation']['is_valid']}")
        if not result['premise_validation']['is_valid']:
            print(f"  Correction: {result['premise_validation']['correction']}")
        print(f"  Concept Bridges: {result['concept_bridges']}")
        print("-" * 50)
