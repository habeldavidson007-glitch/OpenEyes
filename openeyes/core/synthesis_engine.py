"""
openeyes/core/synthesis_engine.py

The 'Brain' that connects facts into arguments.
Transforms a bag of fragments into a coherent, logically structured narrative.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class LogicalNode:
    fragment_id: str
    content: str
    role: str  # 'PREMISE', 'EVIDENCE', 'CONCLUSION', 'CONTEXT'
    confidence: float
    connections: List[str]  # IDs of connected nodes

class SynthesisEngine:
    """
    Converts retrieved fragments into a structural narrative.
    Instead of listing facts, it builds an argument chain: Premise -> Evidence -> Conclusion.
    """
    
    def __init__(self):
        # Logical connectors that indicate causality or contrast
        self.causal_markers = [
            "because", "therefore", "thus", "consequently", "leads to", 
            "results in", "causes", "due to", "since", "as a result"
        ]
        self.contrast_markers = [
            "however", "but", "although", "despite", "conversely", "on the other hand"
        ]

    def synthesize(self, query: str, fragments: List[Dict]) -> str:
        """
        Main entry point. Takes raw fragments and returns a structured narrative.
        """
        if not fragments:
            return "No sufficient evidence found to construct a narrative."

        # 1. Analyze and Role-Assign Fragments
        nodes = self._assign_roles(query, fragments)
        
        # 2. Build Logical Connections (The "Graph")
        graph = self._build_dependency_graph(nodes, query)
        
        # 3. Traverse Graph to Generate Narrative
        narrative = self._generate_narrative(graph, query)
        
        return narrative

    def _assign_roles(self, query: str, fragments: List[Dict]) -> List[LogicalNode]:
        """
        Heuristic role assignment based on keywords and position.
        In a full LLM integration, this would be an NLP task.
        Here we use pattern matching for speed and determinism.
        """
        nodes = []
        query_lower = query.lower()
        
        # Detect question type to improve role assignment
        is_what_question = query_lower.startswith('what')
        is_how_question = query_lower.startswith('how')
        is_why_question = query_lower.startswith('why')
        is_side_effect = 'side effect' in query_lower or 'symptom' in query_lower or 'risk' in query_lower
        
        for i, frag in enumerate(fragments):
            content = frag.get('claim', '') or frag.get('text', '')
            conf = frag.get('confidence_score', 0.5)
            content_lower = content.lower()
            
            # Simple heuristic role assignment
            role = 'EVIDENCE' # Default
            
            # If fragment contains causal markers, it might be a conclusion or premise
            if any(m in content_lower for m in self.causal_markers):
                if "therefore" in content_lower or "result" in content_lower or "leads to" in content_lower:
                    role = 'CONCLUSION'
                elif "because" in content_lower or "due to" in content_lower or "since" in content_lower:
                    role = 'PREMISE'
            
            # For side-effect questions, fragments mentioning specific effects are conclusions
            if is_side_effect:
                if any(word in content_lower for word in ['include', 'are', 'may cause', 'can lead', 'risk', 'effect']):
                    role = 'CONCLUSION'
                elif any(word in content_lower for word in ['inhibits', 'blocks', 'reduces', 'mechanism']):
                    role = 'PREMISE'  # Mechanism explanations are premises
            
            # If fragment directly answers the query keywords, boost to Conclusion
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap = query_words & content_words
            if len(overlap) >= 3:
                role = 'CONCLUSION' # Likely the direct answer
            
            nodes.append(LogicalNode(
                fragment_id=f"frag_{i}",
                content=content,
                role=role,
                confidence=conf,
                connections=[]
            ))
        
        return nodes

    def _build_dependency_graph(self, nodes: List[LogicalNode], query: str) -> List[LogicalNode]:
        """
        Connects nodes logically.
        Strategy: Connect Premises -> Evidence -> Conclusion.
        """
        premises = [n for n in nodes if n.role == 'PREMISE']
        evidence = [n for n in nodes if n.role == 'EVIDENCE']
        conclusions = [n for n in nodes if n.role == 'CONCLUSION']
        
        # Heuristic linking: Connect top evidence to top conclusion
        if conclusions and evidence:
            main_conclusion = max(conclusions, key=lambda x: x.confidence)
            # Link top 3 evidence items to the main conclusion
            sorted_evidence = sorted(evidence, key=lambda x: x.confidence, reverse=True)[:3]
            for ev in sorted_evidence:
                main_conclusion.connections.append(ev.fragment_id)
        
        # Link premises to evidence
        if premises and evidence:
            for ev in evidence[:2]:
                if premises:
                    ev.connections.append(premises[0].fragment_id)
                    
        return nodes

    def _generate_narrative(self, nodes: List[LogicalNode], query: str) -> str:
        """
        Traverses the graph to write a human-readable paragraph.
        """
        conclusions = [n for n in nodes if n.role == 'CONCLUSION']
        evidence = [n for n in nodes if n.role == 'EVIDENCE']
        premises = [n for n in nodes if n.role == 'PREMISE']
        
        if not conclusions and not evidence:
            # Fallback to simple concatenation if logic fails
            return " ".join([n.content for n in nodes])

        narrative_parts = []
        
        # 1. Start with Context/Premise (The "Why")
        if premises:
            narrative_parts.append(f"Based on established principles, {premises[0].content.lower()}")
        
        # 2. Add Evidence with proper connectors (The "What")
        for i, ev in enumerate(evidence[:3]):
            if i == 0:
                connector = "Specifically, "
            elif i == 1:
                connector = "Additionally, "
            else:
                connector = "Furthermore, "
            narrative_parts.append(f"{connector}{ev.content}")
        
        # 3. End with Conclusion (The "Answer")
        if conclusions:
            main_conc = max(conclusions, key=lambda x: x.confidence)
            # Check if we have supporting evidence to link
            if main_conc.connections:
                narrative_parts.append(f"Therefore, {main_conc.content.lower()}")
            else:
                narrative_parts.append(f"In conclusion, {main_conc.content.lower()}")
        elif evidence:
            # If no explicit conclusion, synthesize one from evidence
            last_ev = evidence[-1]
            narrative_parts.append(f"This indicates that {last_ev.content.lower()}")

        # Join and clean up
        full_text = " ".join(narrative_parts)
        
        # Basic cleanup for flow - fix double spaces and ensure proper punctuation
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        # Ensure proper sentence endings
        if full_text and not full_text.endswith('.'):
            full_text += '.'
            
        return full_text
