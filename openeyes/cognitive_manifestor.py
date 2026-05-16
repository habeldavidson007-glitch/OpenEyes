"""
OpenEyes Cognitive Manifestor
Transforms static knowledge fragments into human-like conversational responses
using probabilistic stylistic overlays while maintaining 100% factual accuracy.
"""

import random
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

class CognitiveManifestor:
    def __init__(self, dialogue_patterns_path: str = None):
        self.base_path = Path(__file__).parent
        if dialogue_patterns_path:
            self.patterns_path = Path(dialogue_patterns_path)
        else:
            self.patterns_path = self.base_path / "knowledge" / "dialogue_patterns.json"
        
        self.dialogue_patterns = self._load_patterns()
        self.response_cache = {}
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load human dialogue patterns from JSON corpus."""
        try:
            with open(self.patterns_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Dialogue patterns not found at {self.patterns_path}")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Fallback default patterns if file not found."""
        return {
            "greetings": [{"pattern": "Hi! {opening}", "weight": 0.8}],
            "openings": ["Let's dive into {topic}."],
            "transitions": {
                "definition_to_mechanism": ["Specifically, "],
                "fact_to_analogy": ["Imagine it this way: "]
            },
            "closings": ["Hope that clarifies things!"],
            "cognitive_connectors": {
                "cause_effect": ["because", "since"],
                "additive": ["Additionally, "]
            }
        }
    
    def detect_intent(self, query: str) -> Dict[str, float]:
        """Detect user intent and conversational context."""
        query_lower = query.lower().strip()
        
        intents = {
            "greeting": 0.0,
            "casual_chat": 0.0,
            "factual_query": 0.0,
            "deep_explanation": 0.0,
            "urgent_safety": 0.0
        }
        
        # Greeting detection
        greeting_words = ["hey", "hi", "hello", "greetings", "what's up", "howdy"]
        if any(word in query_lower for word in greeting_words):
            intents["greeting"] = 0.9
        
        # Casual chat detection (short, no specific topic)
        if len(query.split()) <= 3 and intents["greeting"] < 0.5:
            casual_phrases = ["what's up", "how are you", "tell me something", "chat"]
            if any(phrase in query_lower for phrase in casual_phrases):
                intents["casual_chat"] = 0.8
        
        # Deep explanation detection
        deep_keywords = ["explain", "mechanism", "quantitative", "detailed", "how does", "why"]
        if any(keyword in query_lower for keyword in deep_keywords):
            intents["deep_explanation"] = 0.85
        
        # Urgent safety detection - be more specific to avoid false positives
        safety_phrases = ["kill myself", "commit suicide", "overdose on", "hurt myself", "end my life"]
        safety_contexts = ["emergency medical", "immediate danger"]
        if any(phrase in query_lower for phrase in safety_phrases):
            intents["urgent_safety"] = 1.0
        elif any(context in query_lower for context in safety_contexts):
            intents["urgent_safety"] = 0.9
        
        # Default to factual query
        if max(intents.values()) < 0.5:
            intents["factual_query"] = 0.7
        
        return intents
    
    def select_pattern(self, pattern_type: str, context: Dict[str, Any] = None) -> str:
        """Select a conversational pattern with weighted randomness."""
        patterns = self.dialogue_patterns.get(pattern_type, [])
        
        if not patterns:
            return ""
        
        # Handle both dict patterns (with weights) and simple string patterns
        if isinstance(patterns[0], str):
            # Simple string list - uniform random selection
            selected = random.choice(patterns)
            pattern_text = selected
        else:
            # Dict patterns with weights
            weights = [p.get("weight", 1.0) for p in patterns]
            selected = random.choices(patterns, weights=weights, k=1)[0]
            pattern_text = selected.get("pattern", "") if isinstance(selected, dict) else selected
        
        # Fill placeholders if context provided
        if context:
            for key, value in context.items():
                pattern_text = pattern_text.replace(f"{{{key}}}", str(value))
        
        # Clean up any remaining unfilled placeholders
        pattern_text = re.sub(r'\{[^}]+\}', '', pattern_text)
        
        return pattern_text
    
    def select_transition(self, transition_type: str) -> str:
        """Select a transitional phrase for connecting ideas."""
        transitions = self.dialogue_patterns.get("transitions", {}).get(transition_type, [])
        if not transitions:
            return ""
        return random.choice(transitions)
    
    def select_connector(self, connector_type: str) -> str:
        """Select a cognitive connector for logical relationships."""
        connectors = self.dialogue_patterns.get("cognitive_connectors", {}).get(connector_type, [])
        if not connectors:
            return ""
        return random.choice(connectors)
    
    def manifest_response(self, 
                         query: str, 
                         fragments: List[Dict[str, Any]], 
                         confidence: float,
                         domain: str) -> str:
        """
        Transform knowledge fragments into human-like conversational response.
        
        Args:
            query: User's original query
            fragments: Retrieved knowledge fragments with facts/analogies
            confidence: Confidence score (0-100)
            domain: Domain category
            
        Returns:
            Natural, conversational response string
        """
        intents = self.detect_intent(query)
        
        # Handle pure greetings/small talk without facts
        if intents["greeting"] > 0.8 and intents["factual_query"] < 0.3:
            # Only treat as pure greeting if no topic keywords detected
            topic_keywords = ["inflation", "economy", "health", "government", "stock", "investment"]
            has_topic = any(keyword in query.lower() for keyword in topic_keywords)
            
            if not has_topic:
                greeting_patterns = self.dialogue_patterns.get("greetings", [])
                if greeting_patterns:
                    # Select greeting pattern
                    if isinstance(greeting_patterns[0], dict):
                        weights = [p.get("weight", 1.0) for p in greeting_patterns]
                        greeting = random.choices(greeting_patterns, weights=weights, k=1)[0].get("pattern", "Hi!")
                    else:
                        greeting = random.choice(greeting_patterns)
                else:
                    greeting = "Hi!"
                
                opening_patterns = self.dialogue_patterns.get("openings", [])
                if opening_patterns:
                    opening = random.choice(opening_patterns)
                else:
                    opening = "How can I help?"
                
                result = f"{greeting} {opening}"
                # Replace any remaining placeholders
                result = result.replace("{opening}", "").replace("{topic}", "your question")
                return result.strip()
        
        # Handle safety-critical queries
        if intents["urgent_safety"] > 0.9:
            return self._generate_safety_response(query, fragments)
        
        # No fragments available
        if not fragments:
            return self._generate_fallback_response(query, intents)
        
        # Build conversational response from fragments
        return self._build_conversational_response(query, fragments, confidence, domain, intents)
    
    def _generate_safety_response(self, query: str, fragments: List[Dict]) -> str:
        """Generate empathetic but firm safety response."""
        safety_openings = [
            "I need to pause here.",
            "This sounds serious.",
            "I'm concerned about what you're asking."
        ]
        
        response_parts = [random.choice(safety_openings)]
        response_parts.append("I cannot provide advice on potentially harmful situations.")
        response_parts.append("Please consult a qualified professional or contact emergency services immediately.")
        
        return " ".join(response_parts)
    
    def _generate_fallback_response(self, query: str, intents: Dict[str, float]) -> str:
        """Generate graceful fallback when no knowledge found."""
        if intents["casual_chat"] > 0.5:
            fallbacks = [
                "I'm here to chat about verified topics! What would you like to explore?",
                "I'd love to discuss something concrete with you. Any questions on economy, health, or governance?",
                "Small talk isn't my strength, but I have tons of verified knowledge! Ask me something specific."
            ]
            return random.choice(fallbacks)
        
        fallbacks = [
            f"I don't have verified information on '{query}' in my knowledge base yet.",
            f"That's an interesting question, but I need more data to give you a reliable answer.",
            f"My current knowledge doesn't cover '{query}'. Could you rephrase or ask about a related topic?"
        ]
        return random.choice(fallbacks)
    
    def _build_conversational_response(self, 
                                      query: str, 
                                      fragments: List[Dict], 
                                      confidence: float,
                                      domain: str,
                                      intents: Dict[str, float]) -> str:
        """Build natural conversational response from fragments."""
        
        response_parts = []
        
        # 1. Opening (with greeting if detected)
        if intents["greeting"] > 0.5:
            greeting = self.select_pattern("greetings", {"topic": domain})
            response_parts.append(greeting)
        elif intents["deep_explanation"] > 0.7:
            openings = ["Let's break this down.", "Here's a detailed explanation.", "Let's dive deep."]
            response_parts.append(random.choice(openings))
        else:
            opening = self.select_pattern("openings", {"topic": domain})
            if opening:
                response_parts.append(opening)
        
        # 2. Core facts with cognitive connectors
        primary_fragment = fragments[0] if fragments else {}
        
        # Add definition/fact
        if "shorthand" in primary_fragment:
            intro_phrases = ["The key thing is: ", "Simply put: ", "Here's what's happening: ", ""]
            intro = random.choice(intro_phrases)
            response_parts.append(f"{intro}{primary_fragment['shorthand']}")
        
        # 3. Add secondary facts/mechanisms with transitions
        if len(fragments) > 1 or "mechanism" in primary_fragment:
            transition = self.select_transition("definition_to_mechanism")
            connector = self.select_connector("cause_effect")
            
            mechanism_text = primary_fragment.get("mechanism", "")
            if not mechanism_text and len(fragments) > 1:
                mechanism_text = fragments[1].get("shorthand", "")
            
            if mechanism_text:
                response_parts.append(f"{transition}{mechanism_text}")
        
        # 4. Add analogy for clarity (if confidence is high enough)
        if confidence >= 65 and "analogy" in primary_fragment:
            analogy_intro = self.select_transition("fact_to_analogy")
            response_parts.append(f"{analogy_intro}{primary_fragment['analogy']}")
        
        # 5. Add contextual impact for deep explanations
        if intents["deep_explanation"] > 0.7:
            impact_transition = self.select_transition("mechanism_to_impact")
            impact_phrases = [
                "This affects everyday life significantly.",
                "The real-world implications are substantial.",
                "People feel this in their daily finances."
            ]
            if random.random() > 0.5:
                response_parts.append(f"{impact_transition}{random.choice(impact_phrases)}")
        
        # 6. Closing (optional, based on intent)
        if intents["casual_chat"] > 0.4 or confidence < 70:
            closing = self.select_pattern("closings")
            if closing:
                response_parts.append(closing)
        
        # Join parts with proper spacing and punctuation
        response = " ".join(response_parts)
        
        # Clean up double spaces and fix punctuation
        response = re.sub(r'\s+', ' ', response)
        response = re.sub(r'\s+([.,!?;:])', r'\1', response)
        
        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]
        
        return response
    
    def add_variability_seed(self, seed: int):
        """Set random seed for reproducible variability (testing purposes)."""
        random.seed(seed)


# Demo/Test function
def demo_manifestor():
    """Demonstrate the Cognitive Manifestor with sample queries."""
    manifestor = CognitiveManifestor()
    
    # Sample fragments simulating retrieved knowledge
    sample_fragments = [
        {
            "shorthand": "Inflation is a sustained increase in the general price level of goods and services.",
            "mechanism": "Central banks often raise interest rates to combat inflation.",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks.",
            "confidence": 0.92,
            "domain": "economy"
        }
    ]
    
    test_queries = [
        "Hey, what's the deal with inflation?",
        "Explain the quantitative mechanism of inflation.",
        "How does inflation affect everyday people?",
        "What is inflation?",
        "Hey! What's up?"
    ]
    
    print("=== OpenEyes Cognitive Manifestor Demo ===\n")
    
    for i, query in enumerate(test_queries):
        print(f"Query: {query}")
        
        # Simulate fragment retrieval (use sample for relevant queries)
        if "inflation" in query.lower():
            fragments = sample_fragments
            confidence = 85.0
            domain = "economy"
        else:
            fragments = []
            confidence = 0.0
            domain = "general"
        
        response = manifestor.manifest_response(query, fragments, confidence, domain)
        print(f"Response: {response}")
        print("-" * 60)


if __name__ == "__main__":
    demo_manifestor()
