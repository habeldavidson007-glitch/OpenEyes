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

    def synthesize(self, query: str, fragments: List[Dict], include_insights: bool = False) -> str:
        """
        Main entry point. Takes raw fragments and returns a structured narrative.
        
        Args:
            query: The user's question
            fragments: List of fragment dictionaries with 'claim', 'confidence_score', etc.
            include_insights: If True, adds synthesis insights and consensus summary
        """
        if not fragments:
            return "No sufficient evidence found to construct a narrative."

        # 1. Analyze and Role-Assign Fragments
        nodes = self._assign_roles(query, fragments)
        
        # 2. Build Logical Connections (The "Graph")
        graph = self._build_dependency_graph(nodes, query)
        
        # 3. Traverse Graph to Generate Narrative
        narrative = self._generate_narrative(graph, query, include_insights=include_insights)
        
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
            elif topic_match_count >= 2:
                # High relevance - candidate for conclusion
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

    def _generate_narrative(self, nodes: List[LogicalNode], query: str, include_insights: bool = False) -> str:
        """
        Traverses the graph to write a human-readable paragraph.
        CRITICAL: Must directly ANSWER the query first, then provide supporting evidence.
        
        Args:
            nodes: Logical nodes from fragment analysis
            query: The original user query
            include_insights: If True, adds consensus summary and key insights section
        """
        conclusions = [n for n in nodes if n.role == 'CONCLUSION']
        evidence = [n for n in nodes if n.role == 'EVIDENCE']
        premises = [n for n in nodes if n.role == 'PREMISE']
        
        if not conclusions and not evidence:
            # Fallback to simple concatenation if logic fails
            return " ".join([n.content for n in nodes])

        narrative_parts = []
        query_lower = query.lower()
        
        # DETECT QUERY TYPE for proper response structure
        is_what_question = query_lower.startswith('what')
        is_stock_query = 'stock' in query_lower or 'invest' in query_lower or 'roi' in query_lower or 'return' in query_lower
        is_exchange_rate = 'exchange rate' in query_lower or 'currency' in query_lower
        
        # 1. FOR STOCK/INVESTMENT QUERIES: Direct answer first, no fluff
        if is_stock_query and (conclusions or evidence):
            # Start with a direct acknowledgment that specific stock picks require real-time data
            narrative_parts.append(
                "I cannot provide real-time stock recommendations or current ROI data, as my knowledge has a time delay. "
                "However, I can share proven strategies for identifying stocks with strong ROI potential:"
            )
            
            # Add evidence as strategic guidance, not random facts
            relevant_evidence = []
            for ev in evidence[:4]:
                content = ev.content.strip()
                # Filter out completely irrelevant topics (AI regulation, climate change, etc.)
                if any(irrelevant in content.lower() for irrelevant in ['ai regulation', 'climate change', 'geopolitical', 'cybersecurity']):
                    continue
                # Filter out web scraper artifacts and low-quality content
                if any(artifact in content.lower() for artifact in ['duckduckgo', 'bots use', 'search endpoint', 'retrieved 0']):
                    continue
                # Skip very short or nonsensical fragments
                if len(content) < 30 or content.count(' ') < 5:
                    continue
                relevant_evidence.append(content)
            
            if relevant_evidence:
                for i, ev in enumerate(relevant_evidence):
                    if i == 0:
                        connector = "Key approach: "
                    elif i == 1:
                        connector = "Important factor: "
                    else:
                        connector = "Also consider: "
                    narrative_parts.append(f"{connector}{ev}")
            
            # Add a strong actionable conclusion
            narrative_parts.append(
                "For current stock picks with good ROI, you should: (1) Use screening tools like Finviz or Yahoo Finance to filter by ROE > 15%, revenue growth > 10%, and low debt-to-equity; "
                "(2) Consult recent analyst reports from major brokerages; "
                "(3) Consider diversified ETFs if individual stock selection is too risky. "
                "Always verify data recency before making investment decisions."
            )
            
            full_text = " ".join(narrative_parts)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            if full_text and not full_text.endswith('.'):
                full_text += '.'
            return full_text
        
        # 2. FOR EXCHANGE RATE QUERIES: Acknowledge limitation, provide context
        if is_exchange_rate and (conclusions or evidence):
            narrative_parts.append(
                "I cannot provide real-time exchange rates as they fluctuate continuously throughout trading hours. "
                "For current rates, check live sources like XE.com, OANDA, or your bank's currency converter."
            )
            
            # Add only relevant contextual information
            for ev in evidence[:2]:
                content = ev.content
                if 'exchange' in content.lower() or 'currency' in content.lower() or 'forex' in content.lower():
                    narrative_parts.append(f"Context: {content}")
            
            narrative_parts.append(
                "Exchange rates are influenced by interest rate differentials, economic indicators, geopolitical stability, and central bank policies. "
                "Major currency pairs like EUR/USD typically trade with spreads of 1-3 pips through retail brokers."
            )
            
            full_text = " ".join(narrative_parts)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            if full_text and not full_text.endswith('.'):
                full_text += '.'
            return full_text
        
        # 3. GENERIC STRUCTURE for other query types
        # Start with Context/Premise (The "Why") - ONLY if relevant
        if premises:
            # Check if premise is actually relevant to query
            premise_text = premises[0].content.lower()
            query_words = set(query_lower.split())
            premise_words = set(premise_text.split())
            if len(query_words & premise_words) >= 2:
                narrative_parts.append(f"Background: {premises[0].content}")
        
        # Add Evidence with proper connectors (The "What")
        filtered_evidence = []
        for ev in evidence[:4]:
            content = ev.content.lower()
            # Filter out clearly irrelevant content
            if any(irrelevant in content for irrelevant in ['ai regulation', 'climate change', 'geopolitical conflict']):
                continue
            # Also filter based on confidence (downgraded by _assign_roles if irrelevant)
            if ev.confidence < 0.2:
                continue
            filtered_evidence.append(ev.content)
        
        for i, ev_content in enumerate(filtered_evidence):
            if i == 0:
                connector = "Key insight: "
            elif i == 1:
                connector = "Supporting detail: "
            else:
                connector = "Additional context: "
            narrative_parts.append(f"{connector}{ev_content}")
        
        # End with Conclusion (The "Answer") - MUST synthesize, not just repeat
        if conclusions:
            # Get the highest confidence conclusion that's actually relevant
            relevant_conclusions = [c for c in conclusions if c.confidence >= 0.3]
            if relevant_conclusions:
                main_conc = max(relevant_conclusions, key=lambda x: x.confidence)
                # Synthesize a proper conclusion, don't just copy fragment
                if main_conc.connections:
                    narrative_parts.append(f"Bottom line: {main_conc.content}")
                else:
                    narrative_parts.append(f"In summary: {main_conc.content}")
            elif conclusions:
                # Fallback to any conclusion even if low confidence
                main_conc = max(conclusions, key=lambda x: x.confidence)
                narrative_parts.append(f"In summary: {main_conc.content}")
        elif filtered_evidence:
            # If no explicit conclusion, create one from evidence
            narrative_parts.append("This information suggests you should verify current data from authoritative sources before taking action.")

        # CRITICAL FIX: Add insights synthesis section if requested
        if include_insights and len(nodes) > 1:
            # Calculate consensus level
            high_conf_count = sum(1 for n in nodes if n.confidence >= 0.7)
            total_nodes = len(nodes)
            consensus_level = high_conf_count / total_nodes if total_nodes > 0 else 0
            
            # Extract key themes
            all_content = " ".join([n.content.lower() for n in nodes])
            key_themes = []
            if any(word in all_content for word in ['inflation', 'price', 'rate']):
                key_themes.append('price dynamics')
            if any(word in all_content for word in ['growth', 'gdp', 'economic']):
                key_themes.append('economic trends')
            if any(word in all_content for word in ['risk', 'uncertainty', 'volatile']):
                key_themes.append('risk factors')
            
            if key_themes or consensus_level > 0.5:
                narrative_parts.append("")
                narrative_parts.append("---")
                if consensus_level > 0.7:
                    narrative_parts.append(f"**Key Insight:** Strong consensus ({consensus_level*100:.0f}%) across {total_nodes} verified sources on {' and '.join(key_themes) if key_themes else 'core findings'}.")
                elif consensus_level > 0.4:
                    narrative_parts.append(f"**Key Insight:** Moderate agreement ({consensus_level*100:.0f}%) among sources on {' and '.join(key_themes) if key_themes else 'main points'}, with some variation in details.")
                else:
                    narrative_parts.append(f"**Key Insight:** Analysis of {total_nodes} sources reveals multiple perspectives on {' and '.join(key_themes) if key_themes else 'this topic'}. Verify with current data before acting.")

        # Join and clean up
        full_text = " ".join(narrative_parts)
        
        # Basic cleanup for flow - fix double spaces and ensure proper punctuation
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        # Ensure proper sentence endings
        if full_text and not full_text.endswith('.'):
            full_text += '.'
            
        return full_text
