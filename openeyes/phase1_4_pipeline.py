"""
Phases 1-4 Unified Integration Module
Integrates all Phase 1-4 components into a cohesive neuro-symbolic pipeline.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Import Phase components
from openeyes.phase1_lexical_engine import (
    LexicalPriorityEngine, 
    WeightedToken,
    get_lexical_engine,
    process_query_lexical,
    extract_priority_keywords,
    normalize_query_lexical,
)
from openeyes.phase2_domain_router import (
    DomainRouter,
    KnowledgeGraph,
    KnowledgeNode,
    Domain,
    get_domain_router,
    get_knowledge_graph,
    route_query_domain,
)
from openeyes.phase3_boolean_gates import (
    BooleanLogicGateMatrix,
    StateDecayCounter,
    BooleanGateInput,
    BooleanGateResult,
    LogicGateResult,
    get_boolean_gate_matrix,
    get_state_decay_counter,
    evaluate_query_safety,
)
from openeyes.phase4_fuzzy_logic import (
    FuzzyConfidenceEvaluator,
    HumanAnalogyFramer,
    FuzzyConfidenceInput,
    FuzzyConfidenceResult,
    get_fuzzy_confidence_evaluator,
    get_human_analogy_framer,
    calculate_confidence_score,
    frame_answer_with_analogy,
)


@dataclass
class NeuroSymbolicPipelineResult:
    """Complete result from the Phases 1-4 pipeline."""
    # Phase 1 outputs
    weighted_tokens: List[WeightedToken]
    normalized_query: str
    priority_keywords: List[str]
    
    # Phase 2 outputs
    routed_domain: Domain
    domain_confidence: str
    
    # Phase 3 outputs
    gate_result: LogicGateResult
    gate_action: str
    gate_confidence: float
    
    # Phase 4 outputs
    trust_score: float
    confidence_class: str
    response_mode: str
    
    # Final synthesized output
    final_confidence: float
    answer_shorthand: str
    answer_analogy: str
    full_response: str
    
    # Metadata
    processing_time_ms: float = 0.0
    state_depth: int = 0


class NeuroSymbolicPipeline:
    """
    Unified Neuro-Symbolic Pipeline (Phases 1-4)
    
    Processes queries through all four phases:
    1. Lexical Priority Engine - Token weighting, synonym expansion, typo correction
    2. Domain SWITCH Router - O(1) domain extraction
    3. Boolean Logic Gate Matrix - Safety, freshness, validity checks
    4. Fuzzy Logic & Analogy Framing - Confidence scoring, human-readable output
    """
    
    def __init__(self):
        self.lexical_engine = get_lexical_engine()
        self.domain_router = get_domain_router()
        self.boolean_gates = get_boolean_gate_matrix()
        self.fuzzy_evaluator = get_fuzzy_confidence_evaluator()
        self.analogy_framer = get_human_analogy_framer()
        self.state_counter = get_state_decay_counter()
        self.knowledge_graph = get_knowledge_graph()
        
        self._session_id = "default_session"
    
    def set_session(self, session_id: str):
        """Set session ID for state tracking."""
        self._session_id = session_id
        self.state_counter.reset(session_id)
    
    def process_query(self, query: str, domain_hint: Optional[str] = None,
                     fragment_metadata: Optional[Dict[str, Any]] = None) -> NeuroSymbolicPipelineResult:
        """
        Process query through complete Phases 1-4 pipeline.
        
        Args:
            query: Raw user query
            domain_hint: Optional domain hint to guide routing
            fragment_metadata: Optional metadata about retrieved fragments
            
        Returns:
            NeuroSymbolicPipelineResult with all phase outputs
        """
        import time
        start_time = time.time()
        
        # ========== PHASE 1: Lexical Priority Engine ==========
        weighted_tokens = self.lexical_engine.process_query(query, domain_hint or 'general')
        normalized_query = self.lexical_engine.normalize_query(query, domain_hint or 'general')
        priority_keywords = self.lexical_engine.get_priority_keywords(query, domain_hint or 'general', top_n=5)
        
        # ========== PHASE 2: Domain SWITCH Router ==========
        if domain_hint:
            # Use hint but validate against token weights
            routed_domain = self.domain_router.extract_domain(query, priority_keywords)
        else:
            routed_domain = self.domain_router.extract_domain(query, priority_keywords)
        
        domain_confidence = 'high' if routed_domain != Domain.GENERAL else 'low'
        
        # ========== PHASE 3: Boolean Logic Gate Matrix ==========
        # Check state depth
        state_depth = self.state_counter.get_depth(self._session_id)
        
        if state_depth > self.boolean_gates.MAX_STATE_DEPTH:
            # Already exhausted
            gate_result = BooleanGateResult(
                result=LogicGateResult.HALT_EXHAUSTED,
                confidence=0.0,
                message="HALT_EXHAUSTED: Depth limit exceeded",
                action="HALT"
            )
        else:
            # Build gate inputs from fragment metadata
            gate_inputs = BooleanGateInput(
                node_has_token=len(weighted_tokens) > 0 and weighted_tokens[0].weight >= 2.0,
                synonym_matched=any(len(t.synonyms) > 1 for t in weighted_tokens),
                source_is_fresh=fragment_metadata.get('timestamp_fresh', True) if fragment_metadata else True,
                source_is_verified=fragment_metadata.get('verified_source', True) if fragment_metadata else True,
                contains_malicious_input=False,  # Will be checked by gate matrix
                state_depth=state_depth,
                trust_score=fragment_metadata.get('trust_score', 0.95) if fragment_metadata else 0.95,
                domain=routed_domain.name,
                query=query,
            )
            
            # Evaluate through gate matrix
            gate_result = self.boolean_gates.evaluate(
                gate_inputs,
                [t.text for t in weighted_tokens]
            )
            
            # Increment state depth if fallback needed
            if gate_result.result == LogicGateResult.ELSE_FALLBACK:
                state_depth = self.state_counter.increment(self._session_id)
        
        # ========== PHASE 4: Fuzzy Logic & Analogy Framing ==========
        # Calculate fuzzy confidence
        if fragment_metadata:
            fuzzy_inputs = FuzzyConfidenceInput(
                freshness_coefficient=fragment_metadata.get('freshness', 1.0),
                peer_review_status=fragment_metadata.get('verification', 1.0),
                source_ranking=fragment_metadata.get('source_ranking', 1.0),
                contradiction_count=fragment_metadata.get('contradictions', 0),
            )
        else:
            # Default high confidence if no metadata
            fuzzy_inputs = FuzzyConfidenceInput(
                freshness_coefficient=1.0,
                peer_review_status=1.0,
                source_ranking=1.0,
            )
        
        fuzzy_result = self.fuzzy_evaluator.evaluate(fuzzy_inputs)
        
        # Adjust based on gate result
        if gate_result.result == LogicGateResult.IF_MATCH:
            # Boost confidence
            adjusted_trust = min(1.0, fuzzy_result.trust_score + 0.1)
        elif gate_result.result == LogicGateResult.ELSEIF_MATCH:
            # Reduce confidence for stale data
            adjusted_trust = max(0.3, fuzzy_result.trust_score - 0.2)
        elif gate_result.result in [LogicGateResult.HALT_SECURITY, LogicGateResult.HALT_EXHAUSTED]:
            adjusted_trust = 0.0
        else:
            adjusted_trust = fuzzy_result.trust_score
        
        # Generate analogy-framed response
        concept = priority_keywords[0] if priority_keywords else "query topic"
        sample_content = f"Information about {concept} in {routed_domain.name} domain."
        
        framed_response = self.analogy_framer.frame_response(
            concept,
            sample_content,
            routed_domain.name.lower()
        )
        
        # Calculate final confidence
        final_confidence = adjusted_trust * 100  # Convert to percentage
        
        # Determine if we should increment state counter for next query
        if gate_result.result == LogicGateResult.ELSE_FALLBACK:
            # User might refine query, keep state
            pass
        else:
            # Successful resolution, reset state
            self.state_counter.reset(self._session_id)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        return NeuroSymbolicPipelineResult(
            weighted_tokens=weighted_tokens,
            normalized_query=normalized_query,
            priority_keywords=priority_keywords,
            routed_domain=routed_domain,
            domain_confidence=domain_confidence,
            gate_result=gate_result.result,
            gate_action=gate_result.action,
            gate_confidence=gate_result.confidence,
            trust_score=fuzzy_result.trust_score,
            confidence_class=fuzzy_result.confidence_class,
            response_mode=fuzzy_result.response_mode,
            final_confidence=final_confidence,
            answer_shorthand=framed_response['shorthand'],
            answer_analogy=framed_response['analogy'],
            full_response=framed_response['full_response'],
            processing_time_ms=processing_time_ms,
            state_depth=state_depth,
        )


# Singleton instance
_pipeline: Optional[NeuroSymbolicPipeline] = None


def get_neuro_symbolic_pipeline() -> NeuroSymbolicPipeline:
    """Get or create singleton NeuroSymbolicPipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = NeuroSymbolicPipeline()
    return _pipeline


def process_query_full(query: str, **kwargs) -> NeuroSymbolicPipelineResult:
    """
    Convenience function to process query through full pipeline.
    
    Args:
        query: User query
        **kwargs: Additional parameters
        
    Returns:
        NeuroSymbolicPipelineResult
    """
    return get_neuro_symbolic_pipeline().process_query(query, **kwargs)


if __name__ == "__main__":
    # Test integrated pipeline
    print("=" * 80)
    print("PHASES 1-4: INTEGRATED NEURO-SYMBOLIC PIPELINE TEST")
    print("=" * 80)
    
    pipeline = NeuroSymbolicPipeline()
    
    test_queries = [
        ("What causes inflation?", "economy", {'freshness': 0.95, 'verification': 0.90, 'source_ranking': 0.85}),
        ("Is insulin safe for diabetes?", "healthcare", {'freshness': 0.98, 'verification': 0.95, 'source_ranking': 0.92}),
        ("Should I buy stocks now?", "investment", {'freshness': 0.70, 'verification': 0.60, 'source_ranking': 0.65}),
        ("What are new regulations?", "governance", {'freshness': 0.85, 'verification': 0.80, 'source_ranking': 0.75}),
        ("Random unknown query xyz", None, {'freshness': 0.50, 'verification': 0.40, 'source_ranking': 0.45}),
    ]
    
    print("\n--- FULL PIPELINE TESTS ---\n")
    
    for i, (query, domain_hint, metadata) in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        if domain_hint:
            print(f"   Domain Hint: {domain_hint}")
        print("-" * 70)
        
        pipeline.set_session(f"test_session_{i}")
        result = pipeline.process_query(query, domain_hint, metadata)
        
        print(f"   Phase 1 - Normalized: {result.normalized_query}")
        print(f"   Phase 1 - Top Keywords: {', '.join(result.priority_keywords[:3])}")
        print(f"   Phase 2 - Routed Domain: {result.routed_domain.name} ({result.domain_confidence})")
        print(f"   Phase 3 - Gate Result: {result.gate_result.name}")
        print(f"   Phase 3 - Action: {result.gate_action}")
        print(f"   Phase 4 - Trust Score: {result.trust_score:.3f}")
        print(f"   Phase 4 - Confidence: {result.confidence_class}")
        print(f"   Final Confidence: {result.final_confidence:.1f}%")
        print(f"   Shorthand: {result.answer_shorthand}")
        print(f"   Analogy: {result.answer_analogy}")
        print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
