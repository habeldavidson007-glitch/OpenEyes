"""
openeyes/core/synthesis_engine.py

The 'Brain' that connects facts into arguments.
Transforms a bag of fragments into a coherent, logically structured narrative.
CRITICAL UPDATE: Answers must be DIRECT and HUMAN-LIKE, not robotic fact dumps.
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
    CRITICAL: Must answer like a human expert - direct, concise, then supporting details.
    NOT a robot listing facts without answering the question.
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
        CRITICAL: Start with a DIRECT ANSWER, then provide context/evidence.
        """
        if not fragments:
            return "I don't have enough information to answer this question confidently."

        # 1. Analyze and Role-Assign Fragments
        nodes = self._assign_roles(query, fragments)
        
        # 2. Build Logical Connections (The "Graph")
        graph = self._build_dependency_graph(nodes, query)
        
        # 3. Traverse Graph to Generate Narrative - HUMAN-LIKE OUTPUT
        narrative = self._generate_narrative(graph, query)
        
        return narrative

    def _assign_roles(self, query: str, fragments: List[Dict]) -> List[LogicalNode]:
        """
        Heuristic role assignment based on keywords and position.
        Prioritize fragments that directly answer the query.
        CRITICAL: For definition questions, the first high-confidence fragment should be CONCLUSION.
        """
        nodes = []
        query_lower = query.lower()
        
        # Detect question type to improve role assignment
        is_what_question = query_lower.startswith('what')
        is_how_question = query_lower.startswith('how')
        is_why_question = query_lower.startswith('why')
        is_side_effect = 'side effect' in query_lower or 'symptom' in query_lower or 'risk' in query_lower
        
        # Extract key topic words from query for relevance scoring
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'do', 'does', 'did', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'can', 'current', 'that', 'which', 'who', 'whom'}
        query_topics = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]
        
        for i, frag in enumerate(fragments):
            content = frag.get('claim', '') or frag.get('text', '')
            conf = frag.get('confidence_score', 0.5)
            content_lower = content.lower()
            
            # Simple heuristic role assignment
            role = 'EVIDENCE' # Default
            
            # RELEVANCE CHECK: If fragment doesn't mention query topics, mark as low-priority evidence
            topic_match_count = sum(1 for topic in query_topics if topic in content_lower)
            if topic_match_count == 0 and len(query_topics) > 1:
                # Fragment is likely irrelevant - skip it or mark as very low confidence
                conf = conf * 0.3  # Severely downgrade confidence
                role = 'EVIDENCE'  # Keep as evidence but with low weight
            elif topic_match_count >= 1 and conf >= 0.7:
                # High relevance + high confidence - candidate for conclusion
                role = 'CONCLUSION'
            
            # CRITICAL FIX: For "What is X?" questions, first fragment mentioning the term is the answer
            if is_what_question and i == 0 and conf >= 0.7:
                # First high-confidence fragment in a "what" question is typically the definition/answer
                role = 'CONCLUSION'
            
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
            if len(overlap) >= 2:  # Reduced from 3 to 2 for better detection
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
        CRITICAL: Must directly ANSWER the query first, then provide supporting evidence.
        HUMAN-LIKE OUTPUT: Direct, conversational, not robotic.
        """
        conclusions = [n for n in nodes if n.role == 'CONCLUSION']
        evidence = [n for n in nodes if n.role == 'EVIDENCE']
        premises = [n for n in nodes if n.role == 'PREMISE']
        
        if not conclusions and not evidence:
            # Fallback to simple concatenation if logic fails
            return "I don't have enough information to answer this question confidently."

        query_lower = query.lower()
        
        # DETECT QUERY TYPE for proper response structure
        is_what_question = query_lower.startswith('what')
        is_how_question = query_lower.startswith('how')
        is_why_question = query_lower.startswith('why')
        is_stock_query = 'stock' in query_lower or 'invest' in query_lower or 'roi' in query_lower or 'return' in query_lower
        is_exchange_rate = 'exchange rate' in query_lower or 'currency' in query_lower
        is_definition = is_what_question and ('is' in query_lower or 'are' in query_lower)
        
        # ==================== SPECIAL HANDLING FOR STOCKS/EXCHANGE RATES ====================
        if is_stock_query and (conclusions or evidence):
            return self._handle_stock_query(query, conclusions, evidence)
        
        if is_exchange_rate and (conclusions or evidence):
            return self._handle_exchange_rate_query(query, conclusions, evidence)
        
        # ==================== GENERAL HUMAN-LIKE RESPONSE STRUCTURE ====================
        # For definition/direct questions: START WITH THE ANSWER
        if is_definition or is_what_question:
            return self._generate_direct_answer(query, conclusions, evidence, premises)
        
        # For how/why questions: Provide explanation structure
        if is_how_question or is_why_question:
            return self._generate_explanatory_answer(query, conclusions, evidence, premises)
        
        # Default: balanced approach
        return self._generate_balanced_answer(query, conclusions, evidence, premises)
    
    def _handle_stock_query(self, query: str, conclusions: List[LogicalNode], evidence: List[LogicalNode]) -> str:
        """Handle stock/investment queries with appropriate disclaimers."""
        parts = []
        
        # Start with honest limitation
        parts.append("I can't provide real-time stock recommendations or current ROI data since my knowledge isn't live.")
        
        # Add strategic guidance from evidence
        relevant_evidence = []
        for ev in evidence[:4]:
            content = ev.content.strip()
            # Filter out completely irrelevant topics
            if any(irrelevant in content.lower() for irrelevant in ['ai regulation', 'climate change', 'geopolitical', 'cybersecurity']):
                continue
            # Filter out web scraper artifacts
            if any(artifact in content.lower() for artifact in ['duckduckgo', 'bots use', 'search endpoint', 'retrieved 0']):
                continue
            # Skip very short or nonsensical fragments
            if len(content) < 30 or content.count(' ') < 5:
                continue
            relevant_evidence.append(content)
        
        if relevant_evidence:
            parts.append("Here's what to look for when identifying stocks with strong ROI potential:")
            for i, ev in enumerate(relevant_evidence):
                if i == 0:
                    parts.append(f"• {ev}")
                else:
                    parts.append(f"• Also: {ev}")
        
        # Actionable conclusion
        parts.append("\nFor current picks, you should: (1) Use screening tools like Finviz or Yahoo Finance to filter by ROE > 15%, revenue growth > 10%, and low debt-to-equity; (2) Check recent analyst reports; (3) Consider diversified ETFs if individual stocks are too risky. Always verify data before investing.")
        
        return " ".join(parts)
    
    def _handle_exchange_rate_query(self, query: str, conclusions: List[LogicalNode], evidence: List[LogicalNode]) -> str:
        """Handle exchange rate queries with appropriate disclaimers."""
        parts = []
        
        # Honest limitation first
        parts.append("I can't provide real-time exchange rates—they fluctuate constantly during trading hours.")
        parts.append("For current rates, check XE.com, OANDA, or your bank's currency converter.")
        
        # Add relevant context only
        for ev in evidence[:2]:
            content = ev.content
            if 'exchange' in content.lower() or 'currency' in content.lower() or 'forex' in content.lower():
                parts.append(f"Context: {content}")
        
        # General educational info
        parts.append("Exchange rates are driven by interest rate differentials, economic indicators, geopolitical stability, and central bank policies. Major pairs like EUR/USD typically trade with 1-3 pip spreads through retail brokers.")
        
        return " ".join(parts)
    
    def _generate_direct_answer(self, query: str, conclusions: List[LogicalNode], evidence: List[LogicalNode], premises: List[LogicalNode]) -> str:
        """
        Generate a DIRECT, HUMAN-LIKE answer for definition/what questions.
        STRUCTURE: Direct answer first (1-2 sentences), then supporting details.
        NOT: Long preamble, context dumping, or avoiding the actual answer.
        """
        parts = []
        
        # STEP 1: Find the most direct answer from conclusions
        best_conclusion = None
        if conclusions:
            # Sort by confidence and relevance
            sorted_conclusions = sorted(conclusions, key=lambda x: x.confidence, reverse=True)
            best_conclusion = sorted_conclusions[0]
        
        if best_conclusion:
            # Extract the core answer - be direct
            answer_text = best_conclusion.content.strip()
            
            # Clean up overly long answers (truncate if needed)
            if len(answer_text) > 800:
                # Try to find a natural break point
                break_point = answer_text[:800].rfind('.')
                if break_point > 600:
                    answer_text = answer_text[:break_point+1]
                else:
                    answer_text = answer_text[:800] + "..."
            
            parts.append(answer_text)
        
        # STEP 2: Add key supporting evidence (limit to 2-3 most relevant)
        if evidence and len(parts) > 0:  # Only add evidence if we have an answer
            relevant_evidence = []
            for ev in sorted(evidence, key=lambda x: x.confidence, reverse=True)[:3]:
                content = ev.content.strip()
                # Skip irrelevant content
                if any(irrelevant in content.lower() for irrelevant in ['ai regulation', 'climate change', 'geopolitical conflict']):
                    continue
                if ev.confidence < 0.2:
                    continue
                # Avoid duplicates
                if content not in parts and not any(content in p for p in parts):
                    relevant_evidence.append(content)
            
            if relevant_evidence:
                parts.append("\nKey details:")
                for ev_content in relevant_evidence:
                    parts.append(f"• {ev_content}")
        
        # STEP 3: Add brief context from premises only if truly relevant
        if premises and len(parts) <= 2:  # Don't overload if already comprehensive
            query_words = set(query.lower().split())
            for prem in premises[:1]:
                prem_text = prem.content.lower()
                prem_words = set(prem_text.split())
                if len(query_words & prem_words) >= 3:  # High relevance
                    parts.append(f"\nBackground: {prem.content}")
        
        if not parts:
            return "I don't have enough specific information to answer this question directly."
        
        # Join and clean
        full_text = "\n\n".join(parts)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        # Ensure proper punctuation
        if full_text and not full_text.endswith('.'):
            full_text += '.'
        
        return full_text
    
    def _generate_explanatory_answer(self, query: str, conclusions: List[LogicalNode], evidence: List[LogicalNode], premises: List[LogicalNode]) -> str:
        """
        Generate explanatory answers for how/why questions.
        STRUCTURE: Brief summary, then step-by-step or causal explanation.
        """
        parts = []
        
        # Start with a brief summary/overview
        if conclusions:
            best_conclusion = max(conclusions, key=lambda x: x.confidence)
            summary = best_conclusion.content.strip()
            if len(summary) > 400:
                summary = summary[:400] + "..."
            parts.append(summary)
        
        # Add explanatory evidence
        if evidence:
            relevant_evidence = []
            for ev in sorted(evidence, key=lambda x: x.confidence, reverse=True)[:4]:
                content = ev.content.strip()
                if any(irrelevant in content.lower() for irrelevant in ['ai regulation', 'climate change']):
                    continue
                if ev.confidence < 0.2:
                    continue
                relevant_evidence.append(content)
            
            if relevant_evidence:
                parts.append("\nExplanation:")
                for i, ev_content in enumerate(relevant_evidence):
                    if i == 0:
                        parts.append(f"First, {ev_content}")
                    elif i == 1:
                        parts.append(f"Additionally, {ev_content}")
                    else:
                        parts.append(f"• {ev_content}")
        
        if not parts:
            return "I don't have enough information to explain this thoroughly."
        
        full_text = "\n\n".join(parts)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        if full_text and not full_text.endswith('.'):
            full_text += '.'
        
        return full_text
    
    def _generate_balanced_answer(self, query: str, conclusions: List[LogicalNode], evidence: List[LogicalNode], premises: List[LogicalNode]) -> str:
        """Default balanced approach for other query types."""
        parts = []
        
        # Lead with conclusion if available
        if conclusions:
            best_conclusion = max(conclusions, key=lambda x: x.confidence)
            parts.append(best_conclusion.content)
        
        # Add supporting evidence
        if evidence:
            for ev in sorted(evidence, key=lambda x: x.confidence, reverse=True)[:3]:
                if ev.confidence >= 0.3:
                    parts.append(ev.content)
        
        if not parts:
            return "I don't have sufficient information to answer this question."
        
        full_text = "\n\n".join(parts)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        if full_text and not full_text.endswith('.'):
            full_text += '.'
        
        return full_text
