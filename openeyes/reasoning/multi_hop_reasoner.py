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
        
        # Calculate overall confidence (weighted arithmetic mean, capped at 99.9%)
        confidences = [n.confidence for n in all_nodes if n.confidence > 0]
        if confidences:
            # Use weighted arithmetic mean instead of geometric mean to prevent >100%
            # Weight later nodes slightly less as they accumulate uncertainty
            weights = [1.0 / (i + 1) for i in range(len(confidences))]
            total_weight = sum(weights)
            weighted_sum = sum(c * w for c, w in zip(confidences, weights))
            overall_confidence = min(99.9, (weighted_sum / total_weight) * 100)
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
        """Extract key concepts from query with refined stopword filtering."""
        # Expanded stopword list including domain-specific terms
        stop_words = {
            # Basic English stopwords
            "what", "is", "are", "the", "a", "an", "in", "of", "for", "to", "how", "why", "when", "where",
            "do", "does", "did", "can", "could", "would", "should", "will", "shall", "may", "might",
            "this", "that", "these", "those", "it", "its", "be", "been", "being", "have", "has", "had",
            "and", "or", "but", "if", "then", "else", "than", "so", "as", "at", "by", "from", "on", "with",
            "which", "who", "whom", "whose", "into", "through", "during", "before", "after", "above", "below",
            # Question words
            "explain", "describe", "tell", "me", "about", "define", "definition",
            # Domain-specific low-value words
            "general", "specific", "certain", "various", "different", "same", "other", "another",
            "many", "much", "some", "any", "all", "most", "few", "less", "more",
            # Verbs that don't add semantic value
            "occur", "happen", "become", "seem", "appear", "get", "make", "take", "come", "go",
            # Common nouns without specific meaning
            "thing", "things", "way", "ways", "part", "parts", "kind", "kinds", "type", "types",
            # Auxiliary and modal verbs
            "am", "was", "were", "ve", "ll", "d", "re", "s"
        }
        
        # Simple lemmatization mapping for common verb forms
        lemmatization_map = {
            "causing": "cause", "causes": "cause", "caused": "cause",
            "increasing": "increase", "increases": "increase", "increased": "increase",
            "decreasing": "decrease", "decreases": "decrease", "decreased": "decrease",
            "rising": "rise", "rises": "rise", "rose": "rise",
            "falling": "fall", "falls": "fall", "fell": "fall",
            "running": "run", "runs": "run", "ran": "run",
            "effects": "effect", "affecting": "affect", "affected": "affect",
            "prices": "price", "costs": "cost", "values": "value",
            "markets": "market", "stocks": "stock", "bonds": "bond",
            "economies": "economy", "policies": "policy", "regulations": "regulation",
            "symptoms": "symptom", "diseases": "disease", "treatments": "treatment",
            "institutions": "institution", "banks": "bank", "companies": "company",
        }
        
        words = query.lower().split()
        concepts = []
        
        for word in words:
            # Remove punctuation
            cleaned = word.strip(".,!?;:'\"()[]{}")
            
            # Skip stopwords
            if cleaned in stop_words or len(cleaned) <= 2:
                continue
            
            # Apply lemmatization
            lemma = lemmatization_map.get(cleaned, cleaned)
            
            # Skip if lemma is a stopword
            if lemma in stop_words:
                continue
            
            # Only add if not already present (avoid duplicates)
            if lemma not in concepts:
                concepts.append(lemma)
        
        return concepts[:5]  # Limit to 5 key concepts
    
    # Inference Rules - Fully Implemented
    def _apply_transitive_property(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """
        If A->B and B->C, then A->C.
        Implements transitive inference across evidence nodes.
        """
        # Look for chains of relationships in evidence
        relationships = []
        
        for node in evidence_nodes:
            if node.answer:
                # Detect relationship patterns
                answer_lower = node.answer.lower()
                
                # Pattern: "X causes Y", "X leads to Y", "X results in Y"
                cause_patterns = [
                    (r"(\w+)\s+causes\s+(\w+)", "causes"),
                    (r"(\w+)\s+leads\s+to\s+(\w+)", "leads_to"),
                    (r"(\w+)\s+results\s+in\s+(\w+)", "results_in"),
                    (r"(\w+)\s+increases\s+(\w+)", "increases"),
                    (r"(\w+)\s+decreases\s+(\w+)", "decreases"),
                ]
                
                import re
                for pattern, relation_type in cause_patterns:
                    matches = re.findall(pattern, answer_lower)
                    for match in matches:
                        relationships.append({
                            'from': match[0],
                            'to': match[1],
                            'type': relation_type,
                            'node_id': node.node_id
                        })
        
        # Find transitive chains: A->B and B->C implies A->C
        transitive_inferences = []
        for i, rel1 in enumerate(relationships):
            for j, rel2 in enumerate(relationships):
                if i != j and rel1['to'] == rel2['from']:
                    # Found transitive chain
                    transitive_inferences.append({
                        'from': rel1['from'],
                        'to': rel2['to'],
                        'via': rel1['to'],
                        'chain': f"{rel1['from']} {rel1['type']} {rel1['to']} {rel2['type']} {rel2['to']}",
                        'confidence': min(
                            next((n.confidence for n in evidence_nodes if n.node_id == rel1['node_id']), 70),
                            next((n.confidence for n in evidence_nodes if n.node_id == rel2['node_id']), 70)
                        ) * 0.9  # Penalty for transitive inference
                    })
        
        if transitive_inferences:
            # Generate inference from strongest transitive chain
            best_inference = max(transitive_inferences, key=lambda x: x['confidence'])
            
            return ReasoningNode(
                node_id="inference_transitive",
                step_type=ReasoningStepType.INFERENCE,
                question="What can be inferred through transitive reasoning?",
                answer=f"Through transitive reasoning: {best_inference['chain']}. Therefore, {best_inference['from']} indirectly affects {best_inference['to']} via {best_inference['via']}.",
                confidence=best_inference['confidence'],
                dependencies=[n.node_id for n in evidence_nodes],
                metadata={
                    'inference_type': 'transitive',
                    'chain': best_inference['chain'],
                    'intermediate': best_inference['via']
                }
            )
        
        return None
    
    def _apply_cause_effect_chain(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """
        Link cause-effect relationships into coherent chains.
        Detects causal mechanisms and sequences.
        """
        causal_facts = []
        
        for node in evidence_nodes:
            if node.answer:
                answer_lower = node.answer.lower()
                
                # Detect causal language
                causal_indicators = [
                    "because", "therefore", "thus", "consequently", "as a result",
                    "due to", "caused by", "leads to", "triggers", "produces"
                ]
                
                has_causal = any(indicator in answer_lower for indicator in causal_indicators)
                
                if has_causal:
                    causal_facts.append({
                        'content': node.answer,
                        'confidence': node.confidence,
                        'node_id': node.node_id
                    })
        
        if len(causal_facts) >= 2:
            # Build causal chain narrative
            chain_parts = [fact['content'] for fact in causal_facts[:3]]
            avg_confidence = sum(fact['confidence'] for fact in causal_facts) / len(causal_facts)
            
            return ReasoningNode(
                node_id="inference_causal_chain",
                step_type=ReasoningStepType.INFERENCE,
                question="What is the causal mechanism?",
                answer=f"Causal chain identified: {'; '.join(chain_parts)}. These factors interact in a cause-effect sequence.",
                confidence=min(avg_confidence, 85.0),
                dependencies=[fact['node_id'] for fact in causal_facts],
                metadata={
                    'inference_type': 'causal_chain',
                    'facts_count': len(causal_facts),
                    'chain_elements': chain_parts
                }
            )
        
        return None
    
    def _resolve_contradictions(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> Optional[ReasoningNode]:
        """
        Detect and resolve contradictory evidence using weighted voting.
        Returns resolution when contradictions are found.
        """
        # Extract claims from evidence
        claims = []
        
        for node in evidence_nodes:
            if node.answer:
                # Simple claim extraction (in production, use NLP)
                claims.append({
                    'content': node.answer,
                    'confidence': node.confidence,
                    'node_id': node.node_id,
                    'verified': any(f.get('verified', False) for f in node.evidence_fragments)
                })
        
        # Detect contradictions using keyword opposition
        contradiction_pairs = [
            ("increase", "decrease"),
            ("rise", "fall"),
            ("high", "low"),
            ("positive", "negative"),
            ("causes", "prevents"),
            ("effective", "ineffective"),
            ("safe", "dangerous"),
        ]
        
        detected_contradictions = []
        
        for i, claim1 in enumerate(claims):
            for j, claim2 in enumerate(claims):
                if i >= j:
                    continue
                
                content1_lower = claim1['content'].lower()
                content2_lower = claim2['content'].lower()
                
                for pos_term, neg_term in contradiction_pairs:
                    if (pos_term in content1_lower and neg_term in content2_lower) or \
                       (neg_term in content1_lower and pos_term in content2_lower):
                        
                        # Check if they refer to similar subjects (simplified check)
                        words1 = set(content1_lower.split())
                        words2 = set(content2_lower.split())
                        overlap = len(words1 & words2)
                        
                        if overlap >= 2:  # At least 2 common words suggests same topic
                            detected_contradictions.append({
                                'claim1': claim1,
                                'claim2': claim2,
                                'opposition': (pos_term, neg_term),
                                'overlap_count': overlap
                            })
        
        if detected_contradictions:
            # Resolve using weighted voting based on confidence and verification
            resolutions = []
            
            for contradiction in detected_contradictions:
                claim1 = contradiction['claim1']
                claim2 = contradiction['claim2']
                
                # Weight by confidence and verification status
                score1 = claim1['confidence'] * (1.5 if claim1['verified'] else 1.0)
                score2 = claim2['confidence'] * (1.5 if claim2['verified'] else 1.0)
                
                if score1 > score2:
                    winner, loser = claim1, claim2
                    confidence_penalty = 15.0  # Penalty for unresolved tension
                else:
                    winner, loser = claim2, claim1
                    confidence_penalty = 15.0
                
                resolutions.append({
                    'winner': winner['content'][:100],
                    'loser': loser['content'][:100],
                    'final_confidence': winner['confidence'] - confidence_penalty
                })
            
            # Return contradiction resolution
            resolution_text = "Contradictory evidence detected and resolved. "
            for res in resolutions[:2]:  # Limit to top 2 resolutions
                resolution_text += f"Accepted: '{res['winner']}' over conflicting claim. "
            
            avg_resolution_confidence = sum(r['final_confidence'] for r in resolutions) / len(resolutions)
            
            return ReasoningNode(
                node_id="inference_contradiction_resolution",
                step_type=ReasoningStepType.INFERENCE,
                question="How are contradictory claims resolved?",
                answer=resolution_text,
                confidence=max(50.0, avg_resolution_confidence),
                dependencies=[c['claim1']['node_id'] for c in detected_contradictions] + 
                            [c['claim2']['node_id'] for c in detected_contradictions],
                metadata={
                    'inference_type': 'contradiction_resolution',
                    'contradictions_found': len(detected_contradictions),
                    'resolutions': resolutions
                }
            )
        
        return None
    
    def _merge_evidence(self, evidence_nodes: List[ReasoningNode], query: str, domain: str) -> ReasoningNode:
        """
        Merge multiple evidence sources with quality weighting.
        Always returns a merged result even if other inferences fail.
        """
        if not evidence_nodes:
            return ReasoningNode(
                node_id="inference_merge_empty",
                step_type=ReasoningStepType.INFERENCE,
                question="What does the evidence indicate?",
                answer="Insufficient evidence collected to form a conclusion.",
                confidence=0.0,
                dependencies=[],
                metadata={'sources_merged': 0, 'merge_type': 'empty'}
            )
        
        # Filter nodes with actual answers
        valid_nodes = [n for n in evidence_nodes if n.answer and n.confidence > 0]
        
        if not valid_nodes:
            return ReasoningNode(
                node_id="inference_merge_invalid",
                step_type=ReasoningStepType.INFERENCE,
                question="What does the evidence indicate?",
                answer="Evidence collected but lacks sufficient confidence for synthesis.",
                confidence=30.0,
                dependencies=[n.node_id for n in evidence_nodes],
                metadata={'sources_merged': len(evidence_nodes), 'merge_type': 'low_confidence'}
            )
        
        # Weight answers by confidence and verification
        weighted_answers = []
        total_weight = 0.0
        
        for node in valid_nodes:
            # Base weight from confidence
            weight = node.confidence / 100.0
            
            # Bonus for verified fragments
            verified_bonus = 1.2 if any(f.get('verified', False) for f in node.evidence_fragments) else 1.0
            weight *= verified_bonus
            
            weighted_answers.append({
                'content': node.answer,
                'weight': weight,
                'node_id': node.node_id
            })
            total_weight += weight
        
        # Create merged answer (prioritize high-weight sources)
        weighted_answers.sort(key=lambda x: x['weight'], reverse=True)
        
        # Take top answers that contribute 80% of total weight
        merged_parts = []
        cumulative_weight = 0.0
        
        for wa in weighted_answers[:4]:  # Max 4 sources
            merged_parts.append(wa['content'])
            cumulative_weight += wa['weight']
            
            if cumulative_weight >= total_weight * 0.8:
                break
        
        merged_answer = " ".join(merged_parts)
        
        # Calculate merged confidence
        if valid_nodes:
            avg_confidence = sum(n.confidence for n in valid_nodes) / len(valid_nodes)
            verified_count = sum(1 for n in valid_nodes if any(f.get('verified', False) for f in n.evidence_fragments))
            
            # Bonus for multiple verified sources
            if verified_count >= 2:
                avg_confidence = min(95.0, avg_confidence * 1.1)
        else:
            avg_confidence = 50.0
        
        return ReasoningNode(
            node_id="inference_merge",
            step_type=ReasoningStepType.INFERENCE,
            question="What does combined evidence indicate?",
            answer=merged_answer if merged_answer else "Evidence has been collected and analyzed.",
            confidence=min(90.0, avg_confidence),
            dependencies=[wa['node_id'] for wa in weighted_answers],
            metadata={
                'sources_merged': len(weighted_answers),
                'merge_type': 'weighted_average',
                'total_weight': total_weight,
                'verified_sources': verified_count if valid_nodes else 0
            }
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
