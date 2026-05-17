"""
OpenEyes Reasoning Module
Integrates Symbolic Coordinates, Pre-Flight Critic, and Multi-Hop Reasoning
into a unified deterministic reasoning layer.
"""

from .symbolic_coordinates import SymbolicCoordinateSystem
from .preflight_critic import PreFlightCritic, ValidationStatus
from .multi_hop_reasoner import MultiHopReasoner, ReasoningChain

__all__ = [
    'SymbolicCoordinateSystem',
    'PreFlightCritic', 
    'ValidationStatus',
    'MultiHopReasoner',
    'ReasoningChain',
    'DeterministicReasoningEngine'
]


class DeterministicReasoningEngine:
    """
    Unified deterministic reasoning engine for OpenEyes.
    Combines symbolic coordinates, multi-hop reasoning, and pre-flight validation
    to achieve LLM-like reasoning without hallucinations.
    """
    
    def __init__(self):
        self.coordinate_system = SymbolicCoordinateSystem()
        self.critic = PreFlightCritic()
        self.reasoner = MultiHopReasoner(
            coordinate_system=self.coordinate_system
        )
        
        print("✅ Deterministic Reasoning Engine initialized")
        print("   - Symbolic Coordinate System: Active")
        print("   - Pre-Flight Critic: Active")
        print("   - Multi-Hop Reasoner: Active")
    
    def process_query(self, query: str, domain: str, fragments: list = None) -> dict:
        """
        Process a query through the complete deterministic reasoning pipeline.
        
        Returns dict with:
        - answer: Final answer string
        - confidence: Overall confidence percentage
        - reasoning_trace: Complete reasoning chain
        - validation_report: Pre-flight validation results
        - emergency_detected: Boolean for safety halts
        """
        if fragments is None:
            fragments = []
        
        # Step 1: Check for emergency context using symbolic coordinates
        tokens = query.lower().split()
        activations = self.coordinate_system.map_query_to_coordinates(tokens)
        emergency_detected = self.coordinate_system.detect_emergency_context(activations)
        
        if emergency_detected:
            return {
                'answer': self._get_emergency_response(domain),
                'confidence': 100.0,
                'reasoning_trace': None,
                'validation_report': 'HALT_SAFETY: Emergency context detected',
                'emergency_detected': True,
                'status': 'HALT_SAFETY'
            }
        
        # Step 2: Execute multi-hop reasoning
        reasoning_chain = self.reasoner.reason(query, domain)
        
        # Step 3: Run pre-flight validation
        passed, validation_results = self.critic.validate_answer(
            query=query,
            answer=reasoning_chain.final_answer,
            confidence=reasoning_chain.overall_confidence,
            fragments_used=fragments,
            domain=domain
        )
        
        # Step 4: Generate validation report
        validation_report = self.critic.generate_validation_report(
            query=query,
            answer=reasoning_chain.final_answer,
            confidence=reasoning_chain.overall_confidence,
            fragments_used=fragments,
            domain=domain,
            validation_results=validation_results
        )
        
        # Step 5: Determine final status
        if not passed:
            failed_checks = [r for r in validation_results if r.status == ValidationStatus.FAILED]
            if failed_checks:
                status = f"FAILED_VALIDATION: {failed_checks[0].check_name}"
            else:
                status = "WARNING"
        else:
            status = "SUCCESS"
        
        return {
            'answer': reasoning_chain.final_answer,
            'confidence': reasoning_chain.overall_confidence,
            'reasoning_trace': self.reasoner.generate_reasoning_report(reasoning_chain),
            'validation_report': validation_report,
            'emergency_detected': False,
            'status': status,
            'validation_passed': passed,
            'execution_time_ms': reasoning_chain.execution_time_ms,
            'reasoning_steps': reasoning_chain.total_steps
        }
    
    def _get_emergency_response(self, domain: str) -> str:
        """Return appropriate emergency response."""
        if domain.lower() == 'healthcare':
            return (
                "⚠️ MEDICAL EMERGENCY DETECTED ⚠️\n\n"
                "I cannot provide medical advice for emergency situations. Please:\n"
                "• Call emergency services immediately (911 in US)\n"
                "• Go to the nearest emergency room\n"
                "• Contact a healthcare professional\n\n"
                "This system provides general information only, not medical advice."
            )
        else:
            return (
                "⚠️ HIGH-RISK SITUATION DETECTED ⚠️\n\n"
                "This query involves potentially critical information. "
                "Please consult a qualified professional for guidance specific to your situation."
            )
    
    def analyze_query_semantics(self, query: str) -> dict:
        """
        Analyze query using symbolic coordinates without generating answer.
        Useful for query understanding and routing.
        """
        tokens = query.lower().split()
        activations = self.coordinate_system.map_query_to_coordinates(tokens)
        related = self.coordinate_system.find_related_concepts(tokens, threshold=0.6)
        emergency = self.coordinate_system.detect_emergency_context(activations)
        
        return {
            'activated_concepts': list(activations.keys()),
            'coordinate_activations': {
                concept: {'coordinate': coord, 'weight': weight}
                for concept, (coord, weight) in activations.items()
            },
            'related_concepts': related[:10],
            'emergency_detected': emergency,
            'primary_domain': self._infer_primary_domain(activations)
        }
    
    def _infer_primary_domain(self, activations: dict) -> str:
        """Infer primary domain from coordinate activations."""
        if not activations:
            return 'general'
        
        domain_weights = {
            'healthcare': 0.0,
            'economy': 0.0,
            'governance': 0.0,
            'investment': 0.0,
            'general': 0.0
        }
        
        domain_map = {
            0.0: 'healthcare',
            1.0: 'economy',
            2.0: 'governance',
            3.0: 'investment',
            4.0: 'general'
        }
        
        for concept, (coord, weight) in activations.items():
            domain_idx = round(coord[0])
            domain_name = domain_map.get(domain_idx, 'general')
            domain_weights[domain_name] += weight
        
        # Return domain with highest weight
        return max(domain_weights, key=domain_weights.get)


# Test the unified engine
if __name__ == "__main__":
    engine = DeterministicReasoningEngine()
    
    print("\n" + "=" * 70)
    print("DETERMINISTIC REASONING ENGINE - INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Normal query
    print("\n\n📝 Test 1: Normal Economy Query")
    print("-" * 70)
    result1 = engine.process_query("What is inflation?", "economy", [
        {"content": "Inflation is a sustained increase in general price levels.", "verified": True}
    ])
    print(f"Status: {result1['status']}")
    print(f"Confidence: {result1['confidence']:.1f}%")
    print(f"Emergency: {result1['emergency_detected']}")
    print(f"Answer: {result1['answer'][:100]}...")
    
    # Test 2: Emergency query
    print("\n\n📝 Test 2: Healthcare Emergency Query")
    print("-" * 70)
    result2 = engine.process_query("I'm having stroke symptoms what do I do?", "healthcare", [])
    print(f"Status: {result2['status']}")
    print(f"Confidence: {result2['confidence']:.1f}%")
    print(f"Emergency: {result2['emergency_detected']}")
    print(f"Answer:\n{result2['answer']}")
    
    # Test 3: Semantic analysis
    print("\n\n📝 Test 3: Query Semantic Analysis")
    print("-" * 70)
    analysis = engine.analyze_query_semantics("How does hyperinflation affect stock portfolios?")
    print(f"Activated Concepts: {analysis['activated_concepts']}")
    print(f"Primary Domain: {analysis['primary_domain']}")
    print(f"Emergency Detected: {analysis['emergency_detected']}")
    print(f"Related Concepts: {[c[0] for c in analysis['related_concepts'][:5]]}")
    
    print("\n\n✅ All integration tests completed!")
