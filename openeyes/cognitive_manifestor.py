"""
OpenEyes Cognitive Manifestor
Transforms static knowledge fragments into human-like conversational responses
using probabilistic stylistic variation while maintaining deterministic factual accuracy.
"""

import random
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ToneType(Enum):
    NEUTRAL = "neutral"
    EMPATHETIC = "empathetic"
    URGENT = "urgent"
    EXPLANATORY = "explanatory"
    CASUAL = "casual"

@dataclass
class StylisticVector:
    """Defines how a response should be styled"""
    tone: ToneType
    complexity: float  # 0.0 (simple) to 1.0 (technical)
    use_analogy: bool
    sentence_variety: float  # 0.0 (uniform) to 1.0 (varied)
    formality: float  # 0.0 (casual) to 1.0 (formal)

class DialoguePatternCorpus:
    """Stores human conversational patterns for natural speech generation"""
    
    def __init__(self):
        self.patterns = {
            "greeting": [
                "Hey there! {content}",
                "Hello! {content}",
                "Hi! {content}",
                "Great question! {content}",
                "Thanks for asking! {content}"
            ],
            "explanation_start": [
                "Here's what's happening: {content}",
                "Let me break this down: {content}",
                "The key thing to understand is: {content}",
                "Simply put: {content}",
                "In essence: {content}"
            ],
            "analogy_intro": [
                "Think of it like this: {analogy}",
                "Here's a helpful way to picture it: {analogy}",
                "Imagine it this way: {analogy}",
                "A good analogy is: {analogy}",
                "To make it concrete: {analogy}"
            ],
            "connection_phrases": [
                "This connects to {next_topic} because",
                "Building on that, {next_topic}",
                "Related to this is {next_topic}, where",
                "This also affects {next_topic}, since",
                "Following this logic, {next_topic}"
            ],
            "uncertainty_markers": [
                "Based on available data,",
                "Current evidence suggests,",
                "From what we know,",
                "The consensus indicates,",
                "Research shows,"
            ],
            "safety_transitions": [
                "However, I need to be careful here:",
                "Important note:",
                "Safety first:",
                "Critical consideration:",
                "Please remember:"
            ]
        }
    
    def get_pattern(self, category: str, seed: Optional[int] = None) -> str:
        """Get a random pattern from a category with optional seeded randomness"""
        if seed is not None:
            random.seed(seed)
        patterns = self.patterns.get(category, ["{content}"])
        return random.choice(patterns)

class CognitiveManifestor:
    """
    Transforms knowledge fragments into human-like responses using:
    - Probabilistic stylistic variation (controlled randomness)
    - Deterministic factual accuracy (immutable core facts)
    - Context-aware tone adaptation
    """
    
    def __init__(self):
        self.corpus = DialoguePatternCorpus()
        self.fact_cache: Dict[str, Any] = {}
        
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine appropriate stylistic vector"""
        query_lower = query.lower()
        
        # Detect urgency
        urgency_keywords = ["emergency", "urgent", "now", "immediately", "critical"]
        is_urgent = any(kw in query_lower for kw in urgency_keywords)
        
        # Detect complexity preference
        technical_terms = ["mechanism", "pathway", "quantitative", "statistical", "algorithm"]
        is_technical = any(kw in query_lower for kw in technical_terms)
        
        # Detect casualness
        casual_markers = ["hey", "what's up", "tell me about", "explain like i'm 5"]
        is_casual = any(kw in query_lower for kw in casual_markers)
        
        # Determine tone
        if is_urgent:
            tone = ToneType.URGENT
        elif "hurt" in query_lower or "problem" in query_lower:
            tone = ToneType.EMPATHETIC
        elif is_casual:
            tone = ToneType.CASUAL
        else:
            tone = ToneType.EXPLANATORY
        
        return {
            "tone": tone,
            "complexity": 0.8 if is_technical else 0.3 if is_casual else 0.5,
            "use_analogy": not is_technical and not is_urgent,
            "sentence_variety": 0.7 if is_casual else 0.4,
            "formality": 0.3 if is_casual else 0.7 if is_technical else 0.5,
            "is_urgent": is_urgent
        }
    
    def generate_seed_from_query(self, query: str) -> int:
        """Generate a deterministic seed from query for reproducible variation"""
        return sum(ord(c) for c in query) % 10000
    
    def vary_sentence_structure(self, base_text: str, variety_factor: float, seed: int) -> str:
        """Apply controlled variation to sentence structure without changing meaning"""
        random.seed(seed)
        
        if variety_factor < 0.3:
            return base_text
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', base_text)
        
        if len(sentences) <= 1:
            return base_text
        
        # Optionally reorder sentences if they're independent facts
        if variety_factor > 0.6 and random.random() < 0.3:
            # Keep first sentence fixed, shuffle rest slightly
            if len(sentences) > 2:
                middle = sentences[1:-1]
                random.shuffle(middle)
                sentences = [sentences[0]] + middle + [sentences[-1]]
        
        # Vary connectors
        connectors = [" Additionally,", " Moreover,", " Furthermore,", " Also,", " "]
        varied_sentences = []
        for i, sent in enumerate(sentences):
            if i == 0:
                varied_sentences.append(sent)
            else:
                connector = random.choice(connectors) if variety_factor > 0.5 else " "
                varied_sentences.append(f"{connector}{sent.lower()}" if connector.strip() else sent)
        
        return " ".join(varied_sentences)
    
    def manifest_response(self, 
                         fragments: List[Dict[str, Any]], 
                         query: str,
                         confidence: float,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Transform knowledge fragments into a human-like response.
        
        Args:
            fragments: List of verified knowledge fragments
            query: Original user query
            confidence: Confidence score from retrieval
            context: Additional context (conversation history, etc.)
            
        Returns:
            Natural language response with probabilistic styling but deterministic facts
        """
        if not fragments:
            return "I don't have verified information on that topic."
        
        # Analyze intent for stylistic direction
        intent = self.analyze_intent(query)
        seed = self.generate_seed_from_query(query)
        
        # Extract core facts (IMMUTABLE)
        core_facts = []
        analogies = []
        for frag in fragments[:3]:  # Limit to top 3 fragments
            if 'content' in frag:
                core_facts.append(frag['content'])
            if 'analogy' in frag and intent['use_analogy']:
                analogies.append(frag['analogy'])
        
        if not core_facts:
            return "I have related information but no direct answer."
        
        # Build response with stylistic variation (VARIABLE)
        response_parts = []
        
        # Opening based on tone
        if intent['tone'] == ToneType.URGENT:
            opening = "Important: "
        elif intent['tone'] == ToneType.CASUAL:
            opening = self.corpus.get_pattern("greeting", seed) + " "
        else:
            opening = self.corpus.get_pattern("explanation_start", seed + 1) + " "
        
        # First fact with opening
        first_fact = core_facts[0]
        if intent['complexity'] < 0.4:
            # Simplify language
            first_fact = self._simplify_language(first_fact)
        
        response_parts.append(opening.replace("{content}", first_fact))
        
        # Add remaining facts with connections
        if len(core_facts) > 1:
            for i, fact in enumerate(core_facts[1:], 2):
                connector = self.corpus.get_pattern("connection_phrases", seed + i)
                # Replace placeholder with generic reference
                connector = connector.replace("{next_topic}", "this")
                response_parts.append(f"{connector} {fact.lower()}")
        
        # Add analogy if appropriate
        if analogies and intent['use_analogy']:
            analogy_intro = self.corpus.get_pattern("analogy_intro", seed + 10)
            response_parts.append(analogy_intro.replace("{analogy}", analogies[0]))
        
        # Add uncertainty marker for medium confidence
        if 0.55 <= confidence < 0.75:
            marker = self.corpus.get_pattern("uncertainty_markers", seed + 20)
            response_parts.insert(1, marker)
        
        # Combine and vary structure
        base_response = " ".join(response_parts)
        final_response = self.vary_sentence_structure(
            base_response, 
            intent['sentence_variety'], 
            seed + 30
        )
        
        return final_response
    
    def _simplify_language(self, text: str) -> str:
        """Simplify technical language for general audiences"""
        replacements = {
            "utilize": "use",
            "facilitate": "help",
            "implementation": "setup",
            "methodology": "method",
            "subsequently": "then",
            "approximately": "about",
            "demonstrate": "show",
            "indicate": "suggest",
        }
        
        for complex_word, simple_word in replacements.items():
            text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
        
        return text
    
    def create_safety_response(self, reason: str, resources: List[str]) -> str:
        """Generate empathetic but firm safety responses"""
        seed = self.generate_seed_from_query(reason)
        
        openings = [
            "I need to pause here for your safety.",
            "This requires careful consideration.",
            "I want to make sure you get the right help.",
            "Let's approach this carefully."
        ]
        
        opening = random.Random(seed).choice(openings)
        
        response = f"{opening} {reason}\n\n"
        response += "Recommended next steps:\n"
        for i, resource in enumerate(resources[:3], 1):
            response += f"{i}. {resource}\n"
        
        return response

# Example usage and testing
if __name__ == "__main__":
    manifestor = CognitiveManifestor()
    
    # Test fragments
    test_fragments = [
        {
            "content": "Inflation is a sustained increase in the general price level of goods and services.",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks."
        },
        {
            "content": "Central banks often raise interest rates to combat inflation.",
            "analogy": "Like applying brakes to slow down an overheating economy."
        }
    ]
    
    print("=== OpenEyes Cognitive Manifestor Demo ===\n")
    
    queries = [
        "Hey, what's the deal with inflation?",
        "Explain the mechanism of inflation quantitatively.",
        "How does inflation hurt everyday people?",
        "What is inflation?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        response = manifestor.manifest_response(
            fragments=test_fragments,
            query=query,
            confidence=0.85
        )
        print(f"Response: {response}\n")
        print("-" * 60 + "\n")
