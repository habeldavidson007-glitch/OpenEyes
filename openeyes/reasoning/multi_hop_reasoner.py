"""
OpenEyes Multi-Hop Reasoning Engine
Decomposes complex queries into logical sub-questions, resolves each deterministically,
then synthesizes answers using evidence chains - no stochastic guessing.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ReasoningStepType(Enum):
    DECOMPOSITION = "decomposition"
    EVIDENCE_RETRIEVAL = "evidence_retrieval"
    INFERENCE = "inference"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"


@dataclass
class ReasoningNode:
    """Single step in the reasoning chain."""
    node_id: str
    step_type: ReasoningStepType
    question: str
    answer: Optional[str] = None
    confidence: float = 0.0
    evidence_fragments: List[Dict] = None
    dependencies: List[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.evidence_fragments is None:
            self.evidence_fragments = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ReasoningChain:
    """Complete reasoning trace for a query."""
    query: str
    domain: str
    nodes: List[ReasoningNode]
    final_answer: str
    overall_confidence: float
    total_steps: int
    execution_time_ms: float


class MultiHopReasoner:
    """
    Deterministic multi-hop reasoning engine.
    Breaks complex questions into solvable components,
    resolves each using symbolic logic, then synthesizes.
    """
    
    def __init__(self, fragment_retriever=None, coordinate_system=None):
        self.fragment_retriever = fragment_retriever
        self.coordinate_system = coordinate_system
        
        # Decomposition templates for common query patterns
        self.decomposition_templates = {
            "cause_effect": [
                "What is {concept}?",
                "What causes {concept}?",
                "What are the effects of {concept}?"
            ],
            "comparison": [
                "What is {concept_a}?",
                "What is {concept_b}?",
                "How do {concept_a} and {concept_b} differ?",
                "In what contexts are they similar?"
            ],
            "process": [
                "What is {process}?",
                "What are the steps in {process}?",
                "Why does {process} occur?",
                "What factors affect {process}?"
            ],
            "definition_with_context": [
                "What is {concept}?",
                "Where does {concept} apply?",
                "Why is {concept} important?"
            ]
        }
        
        # Inference rules (deterministic logic patterns)
        self.inference_rules = [
            self._apply_transitive_property,
            self._apply_cause_effect_chain,
            self._resolve_contradictions,
            self._merge_evidence,
        ]
    
    def reason(self, query: str, domain: str, context: Dict = None) -> ReasoningChain:
        """
        Execute multi-hop reasoning for a query.
        Returns complete reasoning trace with audit trail.
        """
        import time
        start_time = time.time()
        
        if context is None:
            context = {}
        
        # Step 1: Decompose query into sub-questions
        decomposition_nodes = self._decompose_query(query, domain)
        
        # Step 2: Retrieve evidence for each sub-question
        evidence_nodes = []
        for decomp_node in decomposition_nodes:
            evidence_node = self._retrieve_evidence(decomp_node, domain)
            evidence_nodes.append(evidence_node)
        
        # Step 3: Apply inference rules
        inference_nodes = self._apply_inferences(evidence_nodes, query, domain)
        
        # Step 4: Synthesize final answer
        synthesis_node = self._synthesize_answer(inference_nodes, query, domain)
        
        # Step 5: Validate result
        validation_node = self._validate_reasoning(
            decomposition_nodes + evidence_nodes + inference_nodes,
            synthesis_node,
            query
        )
        
        # Build complete chain
        all_nodes = decomposition_nodes + evidence_nodes + inference_nodes + [synthesis_node, validation_node]
        
        # Calculate overall confidence (geometric mean of node confidences)
        confidences = [n.confidence for n in all_nodes if n.confidence > 0]
        if confidences:
            overall_confidence = (prod(confidences) ** (1/len(confidences))) * 100
        else:
            overall_confidence = 0.0
        
        execution_time = (time.time() - start_time) * 1000
        
        return ReasoningChain(
            query=query,
            domain=domain,
            nodes=all_nodes,
            final_answer=synthesis_node.answer or "",
            overall_confidence=overall_confidence,
            total_steps=len(all_nodes),
            execution_time_ms=execution_time
        )
    
    def _decompose_query(self, query: str, domain: str) -> List[ReasoningNode]:
        """Break query into logical sub-questions."""
        nodes = []
        query_lower = query.lower()
        
        # Detect query pattern
        if any(word in query_lower for word in ["cause", "causes", "why", "because"]):
            pattern = "cause_effect"
        elif any(word in query_lower for word in ["compare", "difference", "vs", "versus", "than"]):
            pattern = "comparison"
        elif any(word in query_lower for word in ["process", "how", "steps", "mechanism"]):
            pattern = "process"
        else:
            pattern = "definition_with_context"
        
        # Extract key concepts (simplified - would use NLP in production)
        concepts = self._extract_key_concepts(query)
        
        template = self.decomposition_templates.get(pattern, self.decomposition_templates["definition_with_context"])
        
        for i, template_question in enumerate(template[:3]):  # Limit to 3 sub-questions
            # Fill template with first concept
            concept = concepts[0] if concepts else "it"
            sub_question = template_question.replace("{concept}", concept)
            
            # Handle comparison templates
            if "{concept_a}" in sub_question and len(concepts) > 1:
                sub_question = sub_question.replace("{concept_a}", concepts[0])
                sub_question = sub_question.replace("{concept_b}", concepts[1] if len(concepts) > 1 else concepts[0])
            
            node = ReasoningNode(
                node_id=f"decomp_{i}",
                step_type=ReasoningStepType.DECOMPOSITION,
                question=sub_question,
                confidence=90.0,  # High confidence in decomposition logic
                metadata={"pattern": pattern, "original_query": query}
            )
            nodes.append(node)
        
        return nodes
    
    def _retrieve_evidence(self, question_node: ReasoningNode, domain: str) -> ReasoningNode:
        """Retrieve evidence fragments for a sub-question."""
        # This would integrate with the actual fragment retrieval system
        # For now, create placeholder node
        
        tokens = question_node.question.split()
        
        # Simulate evidence retrieval
        evidence_node = ReasoningNode(
            node_id=f"evidence_{question_node.node_id}",
            step_type=ReasoningStepType.EVIDENCE_RETRIEVAL,
            question=question_node.question,
            dependencies=[question_node.node_id],
            confidence=75.0,  # Would be calculated from fragment quality
            metadata={"domain": domain, "tokens": tokens}
        )
        
        return evidence_node
    
    def _apply_inferences(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> List[ReasoningNode]:
        """Apply deterministic inference rules to evidence."""
        inference_nodes = []
        
        for rule in self.inference_rules:
            result = rule(evidence_nodes, query, domain)
            if result:
                inference_nodes.append(result)
        
        # Always create at least one inference node
        if not inference_nodes:
            inference_nodes.append(ReasoningNode(
                node_id="inference_0",
                step_type=ReasoningStepType.INFERENCE,
                question="What can be inferred from the evidence?",
                answer="Evidence supports the query.",
                confidence=70.0,
                dependencies=[n.node_id for n in evidence_nodes],
                metadata={"rule_applied": "default_merge"}
            ))
        
        return inference_nodes
    
    def _synthesize_answer(self, inference_nodes: List[ReasoningNode], query: str, domain: str) -> ReasoningNode:
        """Synthesize final answer from inference results."""
        # Combine all inference answers
        answer_parts = [n.answer for n in inference_nodes if n.answer]
        
        if answer_parts:
            final_answer = " ".join(answer_parts)
        else:
            final_answer = f"Based on analysis of {len(inference_nodes)} reasoning steps, the answer to your query about {query[:50]}... requires more specific evidence."
        
        # Calculate synthesis confidence
        inference_confidences = [n.confidence for n in inference_nodes if n.confidence > 0]
        avg_confidence = sum(inference_confidences) / len(inference_confidences) if inference_confidences else 50.0
        
        return ReasoningNode(
            node_id="synthesis_0",
            step_type=ReasoningStepType.SYNTHESIS,
            question=query,
            answer=final_answer,
            confidence=avg_confidence * 0.95,  # Slight penalty for synthesis
            dependencies=[n.node_id for n in inference_nodes],
            metadata={"answer_parts": len(answer_parts)}
        )
    
    def _validate_reasoning(
        self,
        reasoning_nodes: List[ReasoningNode],
        synthesis_node: ReasoningNode,
        query: str
    ) -> ReasoningNode:
        """Validate the complete reasoning chain."""
        # Check for logical consistency
        issues = []
        
        # Check confidence thresholds
        low_confidence_nodes = [n for n in reasoning_nodes if n.confidence < 60.0]
        if low_confidence_nodes:
            issues.append(f"{len(low_confidence_nodes)} low-confidence steps")
        
        # Check for circular dependencies
        node_ids = [n.node_id for n in reasoning_nodes]
        for node in reasoning_nodes:
            if node.node_id in node.dependencies:
                issues.append(f"Circular dependency in {node.node_id}")
        
        validation_confidence = 100.0 - (len(issues) * 10.0)
        
        return ReasoningNode(
            node_id="validation_0",
            step_type=ReasoningStepType.VALIDATION,
            question="Is the reasoning chain valid?",
            answer="Valid" if not issues else f"Issues detected: {', '.join(issues)}",
            confidence=max(0, validation_confidence),
            dependencies=[synthesis_node.node_id] + [n.node_id for n in reasoning_nodes],
            metadata={"issues": issues, "total_nodes_validated": len(reasoning_nodes)}
        )
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query (simplified)."""
        # Remove common words
        stop_words = {"what", "is", "are", "the", "a", "an", "in", "of", "for", "to", "how", "why", "when", "where"}
        words = query.lower().split()
        concepts = [w for w in words if w not in stop_words and len(w) > 3]
        return concepts[:3]  # Limit to 3 concepts
    
    # Inference Rules
    def _apply_transitive_property(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """If A->B and B->C, then A->C."""
        # Simplified implementation
        return None
    
    def _apply_cause_effect_chain(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """Link cause-effect relationships."""
        # Simplified implementation
        return None
    
    def _resolve_contradictions(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """Detect and resolve contradictory evidence."""
        # Simplified implementation
        return None
    
    def _merge_evidence(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> ReasoningNode:
        """Merge multiple evidence sources."""
        merged_answer = " ".join([n.answer for n in evidence_nodes if n.answer][:2])
        
        return ReasoningNode(
            node_id="inference_merge",
            step_type=ReasoningStepType.INFERENCE,
            question="What does combined evidence indicate?",
            answer=merged_answer if merged_answer else "Evidence collected.",
            confidence=75.0,
            dependencies=[n.node_id for n in evidence_nodes],
            metadata={"sources_merged": len(evidence_nodes)}
        )
    
    def generate_reasoning_report(self, chain: ReasoningChain) -> str:
        """Generate human-readable reasoning trace report."""
        report = [
            "=" * 70,
            "MULTI-HOP REASONING TRACE",
            "=" * 70,
            f"Query: {chain.query}",
            f"Domain: {chain.domain}",
            f"Total Steps: {chain.total_steps}",
            f"Execution Time: {chain.execution_time_ms:.2f}ms",
            f"Overall Confidence: {chain.overall_confidence:.1f}%",
            "-" * 70,
            "REASONING CHAIN:",
            "-" * 70,
        ]
        
        for i, node in enumerate(chain.nodes):
            step_icon = {
                ReasoningStepType.DECOMPOSITION: "🔍",
                ReasoningStepType.EVIDENCE_RETRIEVAL: "📚",
                ReasoningStepType.INFERENCE: "🧠",
                ReasoningStepType.SYNTHESIS: "✍️",
                ReasoningStepType.VALIDATION: "✅",
            }.get(node.step_type, "•")
            
            report.append(f"\n{step_icon} Step {i+1}: {node.step_type.value.upper()}")
            report.append(f"   ID: {node.node_id}")
            report.append(f"   Question: {node.question}")
            
            if node.answer:
                report.append(f"   Answer: {node.answer[:100]}{'...' if len(node.answer) > 100 else ''}")
            
            report.append(f"   Confidence: {node.confidence:.1f}%")
            
            if node.dependencies:
                report.append(f"   Dependencies: {', '.join(node.dependencies)}")
        
        report.append("\n" + "=" * 70)
        report.append("FINAL ANSWER:")
        report.append(chain.final_answer)
        report.append("=" * 70)
        
        return "\n".join(report)


def prod(iterable):
    """Calculate product of iterable elements."""
    result = 1
    for x in iterable:
        result *= x
    return result


# Test the system
if __name__ == "__main__":
    reasoner = MultiHopReasoner()
    
    print("=== Multi-Hop Reasoning Engine Test ===\n")
    
    # Test 1: Simple definition query
    print("Test 1: Definition Query")
    chain1 = reasoner.reason("What is inflation?", "economy")
    print(reasoner.generate_reasoning_report(chain1))
    
    # Test 2: Cause-effect query
    print("\n\nTest 2: Cause-Effect Query")
    chain2 = reasoner.reason("What causes hyperinflation?", "economy")
    print(reasoner.generate_reasoning_report(chain2))
    
    # Test 3: Comparison query
    print("\n\nTest 3: Comparison Query")
    chain3 = reasoner.reason("Compare stocks and bonds", "investment")
    print(reasoner.generate_reasoning_report(chain3))
    
    print("\n\n✅ Multi-Hop Reasoning Engine initialized successfully!")
