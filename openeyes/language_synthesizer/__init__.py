"""
OpenEyes Language Synthesizer — Natural Language Response Generator

Converts fragmented facts into coherent, grammatically correct responses
with proper Subject-Verb-Object structure and query-aware framing.

KEY IMPROVEMENT: Actually ANSWERS the question instead of just listing data.
"""

import re
from typing import List, Dict, Any, Optional, Tuple


class LanguageSynthesizer:
    """
    Synthesizes fragments into natural language responses that DIRECTLY ANSWER the query.
    
    Features:
    - Query intent recognition (opinion, fact, comparison, etc.)
    - Thesis-first answer structure
    - Evidence weaving into supporting arguments
    - Proper paragraph flow with topic sentences
    - No bullet points - essay-style narrative
    """
    
    # Query intent patterns
    OPINION_PATTERNS = [
        r"what\s+do\s+you\s+think",
        r"what\s+is\s+your\s+opinion",
        r"how\s+do\s+you\s+view",
        r"what\s+are\s+your\s+thoughts",
        r"tell\s+me\s+about",
        r"describe",
    ]
    
    FACT_PATTERNS = [
        r"what\s+is",
        r"what\s+are",
        r"define",
        r"explain",
        r"how\s+does",
        r"why\s+does",
        r"when\s+did",
        r"who\s+is",
    ]
    
    COMPARISON_PATTERNS = [
        r"compare",
        r"versus",
        r"vs\.",
        r"difference\s+between",
        r"better\s+than",
    ]
    
    RECOMMENDATION_PATTERNS = [
        r"should\s+i",
        r"what\s+should",
        r"recommend",
        r"suggest",
        r"best\s+way",
        r"best\s+stock",
    ]
    
    def __init__(self):
        self.citation_counter = 0
        self.citation_map = {}
    
    def detect_intent(self, query: str) -> str:
        """Detect the intent of the user's query."""
        query_lower = query.lower()
        
        for pattern in self.OPINION_PATTERNS:
            if re.search(pattern, query_lower):
                return "opinion"
        
        for pattern in self.COMPARISON_PATTERNS:
            if re.search(pattern, query_lower):
                return "comparison"
        
        for pattern in self.RECOMMENDATION_PATTERNS:
            if re.search(pattern, query_lower):
                return "recommendation"
        
        for pattern in self.FACT_PATTERNS:
            if re.search(pattern, query_lower):
                return "fact"
        
        return "general"
    
    def extract_key_topics(self, query: str) -> List[str]:
        """Extract key topics from the query for better synthesis."""
        cleaned = query.lower()
        cleaned = re.sub(r'^(what|how|why|when|where|who|which)\s+(do|does|did|is|are|was|were)?\s*(you|i|we)?\s*', '', cleaned)
        cleaned = re.sub(r'^(think|opinion|view|thoughts|tell|describe|explain|define)\s*(about)?\s*', '', cleaned)
        
        words = cleaned.split()
        stop_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        topics = [w for w in words if w not in stop_words and len(w) > 2]
        return topics[:5]
    
    def synthesize_fragments(
        self, 
        fragments: List[Dict[str, Any]], 
        original_query: str,
        domain: str = "general"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Synthesize fragments into a coherent natural language response that DIRECTLY ANSWERS the query.
        
        Structure:
        1. Direct thesis/answer in first paragraph
        2. Supporting evidence woven into flowing paragraphs
        3. Conclusion that ties back to the original question
        """
        if not fragments:
            return "I don't have enough information to answer this question.", {}
        
        # Detect query intent
        intent = self.detect_intent(original_query)
        
        # Extract key topics
        key_topics = self.extract_key_topics(original_query)
        
        # Sort fragments by score (highest first)
        sorted_fragments = sorted(fragments, key=lambda x: x.get("score", 0), reverse=True)
        
        # Build the response with proper structure
        paragraphs = []
        citation_map = {}
        
        # PARAGRAPH 1: Direct answer/thesis based on intent
        opening = self._create_direct_answer(intent, original_query, sorted_fragments, key_topics, citation_map)
        if opening:
            paragraphs.append(opening)
        
        # PARAGRAPH 2+: Supporting evidence and context (flowing narrative)
        body_paragraphs = self._create_supporting_narrative(sorted_fragments, key_topics, citation_map, intent)
        paragraphs.extend(body_paragraphs)
        
        # FINAL PARAGRAPH: Conclusion
        conclusion = self._create_conclusion(intent, sorted_fragments, key_topics, citation_map)
        if conclusion:
            paragraphs.append(conclusion)
        
        # Join paragraphs with double newlines
        answer = "\n\n".join(paragraphs)
        
        return answer, citation_map
    
    def _create_direct_answer(
        self,
        intent: str,
        original_query: str,
        fragments: List[Dict[str, Any]],
        key_topics: List[str],
        citation_map: Dict[str, int]
    ) -> str:
        """
        Create a DIRECT ANSWER paragraph that addresses the query immediately.
        This is the thesis statement of the response.
        """
        if not fragments:
            return ""
        
        citation_counter = 0
        topic_str = " and ".join(key_topics[:3]) if key_topics else "this topic"
        
        # For opinion questions like "what do you think", start with analytical framing
        if intent == "opinion":
            # Synthesize top 2-3 fragments into a thesis statement
            top_frags = fragments[:min(3, len(fragments))]
            
            # Build a thesis from the highest-scoring fragment
            best_frag = top_frags[0]
            content = self._normalize_sentence(best_frag.get("content", ""))
            
            if content:
                citation_counter += 1
                citation_map[best_frag.get("fragment_id", "unknown")] = citation_counter
                
                # Frame as direct analysis
                opening_sentence = f"My analysis of {topic_str} reveals several critical dynamics. "
                
                # Add the main insight - ensure it starts with capital letter
                main_insight = self._normalize_sentence(best_frag.get("content", ""))
                if main_insight:
                    # Make first letter uppercase if it's not already
                    if main_insight[0].islower():
                        main_insight = main_insight[0].upper() + main_insight[1:]
                    
                    paragraph = opening_sentence + main_insight + f" [{citation_counter}]"
                    
                    # Add 1-2 more supporting points with transitions
                    if len(top_frags) > 1:
                        second_frag = top_frags[1]
                        second_content = self._normalize_sentence(second_frag.get("content", ""))
                        if second_content:
                            citation_counter += 1
                            citation_map[second_frag.get("fragment_id", "unknown")] = citation_counter
                            
                            # Ensure proper capitalization for transition
                            if second_content[0].islower():
                                second_content = second_content[0].upper() + second_content[1:]
                            
                            paragraph += f" Furthermore, {second_content} [{citation_counter}]"
                    
                    return paragraph
        
        # For fact questions, provide direct explanation
        elif intent == "fact":
            best_frag = fragments[0]
            content = self._normalize_sentence(best_frag.get("content", ""))
            
            if content:
                citation_counter += 1
                citation_map[best_frag.get("fragment_id", "unknown")] = citation_counter
                return f"Regarding {topic_str}, here are the key facts: {content} [{citation_counter}]"
        
        # For recommendation questions (like "best stock"), be direct about limitations
        elif intent == "recommendation":
            # OpenEyes doesn't give financial advice, so frame appropriately
            return f"I cannot provide specific investment recommendations, but I can share relevant analysis about {topic_str} based on verified data."
        
        # For comparison questions
        elif intent == "comparison":
            best_frag = fragments[0]
            content = self._normalize_sentence(best_frag.get("content", ""))
            
            if content:
                citation_counter += 1
                citation_map[best_frag.get("fragment_id", "unknown")] = citation_counter
                return f"In comparing these aspects, the evidence shows: {content} [{citation_counter}]"
        
        # Default: general analytical opening
        else:
            best_frag = fragments[0]
            content = self._normalize_sentence(best_frag.get("content", ""))
            
            if content:
                citation_counter += 1
                citation_map[best_frag.get("fragment_id", "unknown")] = citation_counter
                return f"Analysis of {topic_str} indicates: {content} [{citation_counter}]"
        
        return ""
    
    def _create_supporting_narrative(
        self,
        fragments: List[Dict[str, Any]],
        key_topics: List[str],
        citation_map: Dict[str, int],
        intent: str
    ) -> List[str]:
        """
        Create flowing body paragraphs that weave evidence into a coherent narrative.
        Each paragraph should have a topic sentence and flow naturally to the next.
        """
        paragraphs = []
        
        if len(fragments) < 2:
            return paragraphs
        
        # Skip the first fragment(s) already used in direct answer
        remaining_frags = fragments[2:] if intent == "opinion" else fragments[1:]
        
        if not remaining_frags:
            return paragraphs
        
        # Group remaining fragments thematically
        thematic_groups = self._group_by_theme(remaining_frags, key_topics)
        
        citation_counter = max(citation_map.values()) if citation_map else 0
        
        # Transition phrases for connecting ideas
        paragraph_transitions = [
            "A critical aspect to consider is that",
            "Beyond this,",
            "In addition,",
            "Another important dimension involves",
            "The broader context shows that",
            "Market dynamics further reveal that",
            "Research indicates that",
            "Historical patterns suggest that"
        ]
        
        for i, (theme, group_frags) in enumerate(thematic_groups.items()):
            if not group_frags:
                continue
            
            paragraph_parts = []
            
            # Start with a transition (except first body paragraph)
            if i > 0 and i - 1 < len(paragraph_transitions):
                paragraph_parts.append(paragraph_transitions[i - 1])
            
            # Process top 2-3 fragments in this theme
            for j, frag in enumerate(group_frags[:3]):
                content = self._normalize_sentence(frag.get("content", ""))
                if not content:
                    continue
                
                citation_counter += 1
                citation_map[frag.get("fragment_id", "unknown")] = citation_counter
                
                # For first fragment in paragraph, ensure proper capitalization after transition
                if j == 0 and paragraph_parts and paragraph_parts[-1].endswith('that'):
                    if content[0].isupper():
                        content = content[0].lower() + content[1:]
                    paragraph_parts.append(content + f" [{citation_counter}]")
                else:
                    # Add with appropriate connector
                    if j > 0:
                        connectors = ["Additionally,", "Moreover,", "This is evident in that"]
                        connector = connectors[min(j - 1, len(connectors) - 1)]
                        if content[0].isupper():
                            content = content[0].lower() + content[1:]
                        paragraph_parts.append(f"{connector} {content} [{citation_counter}]")
                    else:
                        paragraph_parts.append(f"{content} [{citation_counter}]")
            
            if paragraph_parts:
                # Join into coherent paragraph
                paragraph_text = " ".join(paragraph_parts)
                
                # Ensure proper punctuation between sentences
                paragraph_text = re.sub(r'\]\s+([A-Z])', r'] \1', paragraph_text)
                
                paragraphs.append(paragraph_text)
        
        return paragraphs
    
    def _group_by_theme(
        self,
        fragments: List[Dict[str, Any]],
        key_topics: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group fragments by thematic similarity for better narrative flow."""
        themes = {
            "market_structure": [],
            "economic_indicators": [],
            "investment_strategy": [],
            "risk_factors": [],
            "regulatory_context": [],
            "historical_context": [],
            "other": []
        }
        
        # Keywords for each theme
        theme_keywords = {
            "market_structure": ["market", "trading", "liquidity", "hft", "exchange", "volume"],
            "economic_indicators": ["gdp", "inflation", "rate", "fed", "interest", "employment", "cpi", "pce"],
            "investment_strategy": ["sector", "rotation", "allocation", "portfolio", "diversification", "yield"],
            "risk_factors": ["volatility", "risk", "crash", "decline", "uncertainty", "bubble"],
            "regulatory_context": ["sec", "regulation", "rule", "compliance", "policy", "mandate"],
            "historical_context": ["historical", "trend", "cycle", "pattern", "super cycle", "past"]
        }
        
        for frag in fragments:
            content = frag.get("content", "").lower()
            assigned = False
            
            for theme, keywords in theme_keywords.items():
                if any(kw in content for kw in keywords):
                    themes[theme].append(frag)
                    assigned = True
                    break
            
            if not assigned:
                themes["other"].append(frag)
        
        # Remove empty themes
        return {k: v for k, v in themes.items() if v}
    
    def _group_fragments(
        self, 
        fragments: List[Dict[str, Any]], 
        key_topics: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group fragments by topic relevance (legacy method, kept for compatibility)."""
        groups = {
            "primary": [],
            "supporting": [],
            "context": []
        }
        
        for frag in fragments:
            content = frag.get("content", "").lower()
            relevance_score = sum(1 for topic in key_topics if topic in content)
            
            if relevance_score >= 2:
                groups["primary"].append(frag)
            elif relevance_score == 1:
                groups["supporting"].append(frag)
            else:
                groups["context"].append(frag)
        
        for group_name in groups:
            groups[group_name].sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return groups
    
    def _create_opening(
        self, 
        intent: str, 
        query: str, 
        topics: List[str]
    ) -> str:
        """Create an opening statement based on query intent (legacy method)."""
        if intent == "opinion":
            topic_str = " and ".join(topics[:2]) if topics else "this topic"
            return f"I've analyzed the current landscape regarding {topic_str}. Here's what the evidence suggests:"
        
        elif intent == "fact":
            topic_str = " and ".join(topics[:2]) if topics else "this subject"
            return f"Let me explain {topic_str} based on verified information:"
        
        elif intent == "comparison":
            return "Here's a detailed comparison based on available data:"
        
        elif intent == "recommendation":
            topic_str = " and ".join(topics[:2]) if topics else "your question"
            return f"Regarding {topic_str}, here's my assessment:"
        
        topic_str = " and ".join(topics[:2]) if topics else "your query"
        return f"Based on my analysis of {topic_str}, here are the key insights:"
    
    def _synthesize_group(
        self,
        group_name: str,
        fragments: List[Dict[str, Any]],
        start_citation: int,
        citation_map: Dict[str, int]
    ) -> str:
        """Synthesize a group of fragments into a coherent paragraph with proper narrative flow."""
        if not fragments:
            return ""
        
        # Build a narrative by connecting related concepts
        paragraph_parts = []
        citation_counter = start_citation
        
        # For primary group, create a more detailed narrative
        if group_name == "primary":
            # Take the top 3-5 most relevant fragments and weave them together
            selected_frags = fragments[:min(5, len(fragments))]
            
            # Create topic sentence from the highest-scoring fragment
            if selected_frags:
                best_frag = selected_frags[0]
                content = self._normalize_sentence(best_frag.get("content", ""))
                if content:
                    citation_counter += 1
                    citation_map[best_frag.get("fragment_id", "unknown")] = citation_counter
                    paragraph_parts.append(content + f" [{citation_counter}]")
            
            # Add supporting details with transitional phrases
            transition_phrases = [
                "Furthermore,", "Additionally,", "Moreover,", "In related developments,",
                "This is particularly evident when considering that", "Research also indicates that",
                "Another important aspect is that", "Building on this,"
            ]
            
            for i, frag in enumerate(selected_frags[1:], 1):
                content = self._normalize_sentence(frag.get("content", ""))
                if content:
                    citation_counter += 1
                    citation_map[frag.get("fragment_id", "unknown")] = citation_counter
                    
                    # Add transitional phrase for flow
                    if i < len(transition_phrases):
                        # Ensure content starts with lowercase after transition if it's a continuation
                        if content[0].isupper() and len(content) > 1:
                            content = content[0].lower() + content[1:]
                        paragraph_parts.append(f"{transition_phrases[i-1]} {content} [{citation_counter}]")
                    else:
                        paragraph_parts.append(f"{content} [{citation_counter}]")
        
        # For supporting and context groups, create briefer connected statements
        else:
            for frag in fragments[:3]:  # Limit to top 3 for non-primary groups
                content = self._normalize_sentence(frag.get("content", ""))
                if content:
                    citation_counter += 1
                    citation_map[frag.get("fragment_id", "unknown")] = citation_counter
                    paragraph_parts.append(f"{content} [{citation_counter}]")
        
        if not paragraph_parts:
            return ""
        
        # Join all parts into a single flowing paragraph
        paragraph = " ".join(paragraph_parts)
        
        return paragraph
    
    def _normalize_sentence(self, text: str) -> str:
        """Normalize text into proper sentence structure."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure sentence starts with capital letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure sentence ends with period if it doesn't have punctuation
        if text and text[-1] not in '.!?;:':
            text += '.'
        
        # Fix common grammatical issues
        text = re.sub(r'\b(i)\b', 'I', text)
        text = re.sub(r"\b(dont|cant|wont|shouldnt|couldnt|wouldnt)\b", 
                     lambda m: m.group(1).replace("n't", "n't"), text)
        
        return text
    
    def _create_conclusion(
        self, 
        intent: str,
        fragments: List[Dict[str, Any]],
        key_topics: List[str],
        citation_map: Dict[str, int]
    ) -> str:
        """Create a concluding statement that ties back to the original question."""
        if len(fragments) < 3:
            return ""
        
        topic_str = " and ".join(key_topics[:2]) if key_topics else "these dynamics"
        
        if intent == "opinion":
            return f"This analysis of {topic_str} reflects the current consensus and available evidence from verified sources."
        
        elif intent == "recommendation":
            return f"When evaluating {topic_str}, consider these factors carefully and consult with qualified professionals for personalized advice."
        
        elif intent == "fact":
            return f"These points provide a comprehensive overview of {topic_str} based on verified sources."
        
        elif intent == "comparison":
            return f"Each aspect of {topic_str} has distinct characteristics that should be weighed against your specific needs."
        
        # Default conclusion for general queries
        return f"This summary captures the key aspects of {topic_str} based on available information."
