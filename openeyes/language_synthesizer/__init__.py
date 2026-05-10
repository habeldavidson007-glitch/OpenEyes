"""
OpenEyes Language Synthesizer — Natural Language Response Generator

Converts fragmented facts into coherent, grammatically correct responses
with proper Subject-Verb-Object structure and query-aware framing.
"""

import re
from typing import List, Dict, Any, Optional, Tuple


class LanguageSynthesizer:
    """
    Synthesizes fragments into natural language responses.
    
    Features:
    - Query intent recognition (opinion, fact, comparison, etc.)
    - Sentence structure optimization (SVO order)
    - Coherent paragraph formation
    - Appropriate response framing ("I think", "Based on evidence", etc.)
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
    
    def get_response_frame(self, intent: str) -> str:
        """Get appropriate response framing based on query intent."""
        frames = {
            "opinion": "Based on my analysis, ",
            "fact": "",
            "comparison": "In comparing these aspects, ",
            "recommendation": "Based on the available evidence, ",
            "general": ""
        }
        return frames.get(intent, "")
    
    def extract_key_topics(self, query: str) -> List[str]:
        """Extract key topics from the query for better synthesis."""
        # Remove question words and common phrases
        cleaned = query.lower()
        cleaned = re.sub(r'^(what|how|why|when|where|who|which)\s+(do|does|did|is|are|was|were)?\s*(you|i|we)?\s*', '', cleaned)
        cleaned = re.sub(r'^(think|opinion|view|thoughts|tell|describe|explain|define)\s*(about)?\s*', '', cleaned)
        
        # Split and filter
        words = cleaned.split()
        stop_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        topics = [w for w in words if w not in stop_words and len(w) > 2]
        return topics[:5]  # Return top 5 topics
    
    def synthesize_fragments(
        self, 
        fragments: List[Dict[str, Any]], 
        original_query: str,
        domain: str = "general"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Synthesize fragments into a coherent natural language response.
        
        Args:
            fragments: List of fragment dictionaries with content, source, etc.
            original_query: The user's original query
            domain: Domain context
            
        Returns:
            Tuple of (synthesized_answer, citation_info)
        """
        if not fragments:
            return "I don't have enough information to answer this question.", {}
        
        # Detect query intent
        intent = self.detect_intent(original_query)
        response_frame = self.get_response_frame(intent)
        
        # Extract key topics for coherence
        key_topics = self.extract_key_topics(original_query)
        
        # Group fragments by relevance and content type
        grouped = self._group_fragments(fragments, key_topics)
        
        # Build coherent paragraphs
        paragraphs = []
        citation_map = {}
        citation_counter = 0
        
        # Opening statement based on intent
        opening = self._create_opening(intent, original_query, key_topics)
        if opening:
            paragraphs.append(opening)
        
        # Process each group
        for group_name, group_frags in grouped.items():
            paragraph = self._synthesize_group(
                group_name, 
                group_frags, 
                citation_counter,
                citation_map
            )
            if paragraph:
                paragraphs.append(paragraph)
                citation_counter = max(citation_map.values()) if citation_map else citation_counter
        
        # Create conclusion if needed
        conclusion = self._create_conclusion(intent, grouped)
        if conclusion:
            paragraphs.append(conclusion)
        
        # Join paragraphs
        answer = "\n\n".join(paragraphs)
        
        return answer, citation_map
    
    def _group_fragments(
        self, 
        fragments: List[Dict[str, Any]], 
        key_topics: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group fragments by topic relevance."""
        groups = {
            "primary": [],
            "supporting": [],
            "context": []
        }
        
        for frag in fragments:
            content = frag.get("content", "").lower()
            
            # Check if fragment mentions key topics
            relevance_score = sum(1 for topic in key_topics if topic in content)
            
            if relevance_score >= 2:
                groups["primary"].append(frag)
            elif relevance_score == 1:
                groups["supporting"].append(frag)
            else:
                groups["context"].append(frag)
        
        # Sort each group by score
        for group_name in groups:
            groups[group_name].sort(
                key=lambda x: x.get("score", 0), 
                reverse=True
            )
        
        return groups
    
    def _create_opening(
        self, 
        intent: str, 
        query: str, 
        topics: List[str]
    ) -> str:
        """Create an opening statement based on query intent."""
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
        
        return ""
    
    def _synthesize_group(
        self,
        group_name: str,
        fragments: List[Dict[str, Any]],
        start_citation: int,
        citation_map: Dict[str, int]
    ) -> str:
        """Synthesize a group of fragments into a coherent paragraph."""
        if not fragments:
            return ""
        
        sentences = []
        citation_counter = start_citation
        
        for frag in fragments[:5]:  # Limit to top 5 per group
            content = frag.get("content", "")
            fragment_id = frag.get("fragment_id", "unknown")
            
            # Clean and normalize content
            cleaned = self._normalize_sentence(content)
            
            if cleaned:
                citation_counter += 1
                citation_num = citation_counter
                citation_map[fragment_id] = citation_num
                sentences.append(f"{cleaned} [{citation_num}]")
        
        if not sentences:
            return ""
        
        # Join sentences into paragraph
        paragraph = " ".join(sentences)
        
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
        grouped_fragments: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Create a concluding statement if appropriate."""
        total_frags = sum(len(frags) for frags in grouped_fragments.values())
        
        if total_frags < 3:
            return ""
        
        if intent == "opinion":
            return "This analysis reflects the current consensus and available evidence on the matter."
        
        elif intent == "recommendation":
            return "Consider these factors carefully when making your decision."
        
        return ""
