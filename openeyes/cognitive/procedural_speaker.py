"""
Procedural Speaker - Runtime Integration Layer
Connects verified facts from fragments to the Linguistic Genome for dynamic generation.
Guarantees core facts never change, only the linguistic wrapping varies.
"""

import random
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Add cognitive directory to path
sys.path.insert(0, str(Path(__file__).parent))

from linguistic_genome import LinguisticGenome, AtomicFact


class ProceduralSpeaker:
    """
    The Engine that takes verified text from fragments,
    breaks it down, and runs it through the linguistic genome
    to rebuild it uniquely every time.
    """
    
    def __init__(self, dna_file: str = None):
        self.genome = LinguisticGenome(dna_file=dna_file)
        self.session_id = random.randint(100000, 999999)
        self.generation_count = 0
        self.fact_cache = {}  # Cache deconstructed facts
        
    def _extract_components_from_fragments(self, fragments: List[Any]) -> Dict:
        """
        Extract core components from fragment list.
        Prioritizes high-confidence fragments.
        """
        if not fragments:
            return {"fact": None}
        
        # Sort by confidence if available
        sorted_frags = sorted(
            fragments,
            key=lambda f: getattr(f, 'confidence_score', getattr(f, 'effective_weight', 0.5)),
            reverse=True
        )
        
        components = {
            "fact": None,
            "mechanism": None,
            "impact": None,
            "analogy": None,
            "counterpoint": None,
            "domain": "general"
        }
        
        for frag in sorted_frags[:5]:  # Check top 5 fragments
            content = (
                getattr(frag, "content", "") or 
                getattr(frag, "claim", "") or 
                getattr(frag, "summary", "") or
                getattr(frag, "text", "")
            )
            
            if not content:
                continue
            
            # Extract based on fragment type/metadata
            frag_type_attr = getattr(frag, "fragment_type", None)
            frag_type = frag_type_attr.lower() if frag_type_attr else ""
            
            if not components["fact"]:
                components["fact"] = content
                components["domain"] = getattr(frag, "domain", "general")
            
            # Look for specific component types
            if hasattr(frag, 'mechanism') and frag.mechanism and not components["mechanism"]:
                components["mechanism"] = frag.mechanism
            elif frag_type == "mechanism" and not components["mechanism"]:
                components["mechanism"] = content
            
            if hasattr(frag, 'impact') and frag.impact and not components["impact"]:
                components["impact"] = frag.impact
            elif frag_type == "impact" and not components["impact"]:
                components["impact"] = content
            
            if hasattr(frag, 'analogy') and frag.analogy and not components["analogy"]:
                components["analogy"] = frag.analogy
            elif frag_type == "analogy" and not components["analogy"]:
                components["analogy"] = content
            
            if hasattr(frag, 'counterpoint') and frag.counterpoint and not components["counterpoint"]:
                components["counterpoint"] = frag.counterpoint
        
        return components
    
    def _detect_intent_from_query(self, query: str) -> str:
        """Detect user intent to guide generation style"""
        query_lower = query.lower()
        
        # Urgent concerns
        urgent_keywords = ['emergency', 'urgent', 'critical', 'danger', 'hurt', 'harm', 'stop', 'wrong']
        if any(kw in query_lower for kw in urgent_keywords):
            return 'urgent_concern'
        
        # Technical deep dives
        technical_keywords = ['mechanism', 'quantitative', 'technical', 'formula', 'calculate', 
                             'mathematical', 'empirical', 'algorithm', 'model']
        if any(kw in query_lower for kw in technical_keywords):
            return 'technical_deep_dive'
        
        # Casual queries
        casual_indicators = ['hey', 'what\'s up', 'tell me about', 'what\'s the deal', 
                            'explain like', 'simple', 'basically']
        if any(ind in query_lower for ind in casual_indicators):
            return 'casual_query'
        
        # Educational/exploratory
        if '?' in query or any(kw in query_lower for kw in ['how', 'why', 'what', 'when', 'where']):
            return 'educational'
        
        return 'exploratory'
    
    def speak(self, query: str, fragments: List[Any], **kwargs) -> str:
        """Generate human-like response from verified fragments."""
        if not fragments:
            return "I don't have verified information on that topic."
        
        # Extract fact from fragment (handles both dict and object types)
        fact = None
        analogy = None
        
        for frag in fragments:
            # Handle dict type
            if isinstance(frag, dict):
                if not fact and "content" in frag:
                    fact = frag["content"]
                if not analogy and "analogy" in frag and frag["analogy"]:
                    analogy = frag["analogy"]
            # Handle object type (with attributes)
            else:
                if not fact:
                    fact = getattr(frag, "content", getattr(frag, "claim", getattr(frag, "summary", getattr(frag, "text", None))))
                if not analogy:
                    analogy = getattr(frag, "analogy", None)
        
        if not fact:
            return "I don't have verified information on that topic."
        
        # Detect intent
        intent = self._detect_intent_from_query(query)
        
        # Generate using linguistic genome
        self.generation_count += 1
        
        response = self.genome.generate(
            fact_text=fact,
            mechanism=None,
            impact=None,
            analogy=analogy,
            intent=intent,
            domain="general"
        )
        
        return response
    
    def speak_multiple(self, query: str, fragments: List[Any], 
                       count: int = 3) -> List[str]:
        """
        Generate multiple unique variations of the same fact.
        Useful for A/B testing or showing variety.
        
        Args:
            query: User's question
            fragments: Verified fact fragments
            count: Number of variations to generate
            
        Returns:
            List of unique response variations
        """
        variations = []
        
        for i in range(count):
            self.genome.reset_session()
            variation = self.speak(query, fragments)
            variations.append(variation)
        
        return variations
    
    def get_generation_stats(self) -> Dict:
        """Return statistics about generations in this session"""
        return {
            "session_id": self.session_id,
            "generation_count": self.generation_count,
            "vocabulary_used": len(self.genome.used_vocabulary),
            "patterns_used": len(self.genome.used_patterns)
        }
    
    def reset_session(self):
        """Reset for new conversation"""
        self.genome.reset_session()
        self.session_id = random.randint(100000, 999999)
        self.generation_count = 0
        self.fact_cache.clear()


# Demo and integration test
if __name__ == "__main__":
    print("=== Procedural Speaker Demo ===\n")
    
    speaker = ProceduralSpeaker()
    
    # Mock fragment objects for demo
    class MockFragment:
        def __init__(self, content, domain="economy", confidence=0.8, fragment_type=None):
            self.content = content
            self.domain = domain
            self.confidence_score = confidence
            self.fragment_type = fragment_type
    
    test_scenarios = [
        {
            "query": "Hey, what's the deal with inflation?",
            "fragments": [
                MockFragment("Inflation increases consumer prices by approximately 2-3% annually"),
                MockFragment("Central banks adjust interest rates to manage money supply", 
                           fragment_type="mechanism"),
                MockFragment("Purchasing power decreases for fixed-income households",
                           fragment_type="impact"),
                MockFragment("Your paycheck stays the same but your grocery cart shrinks",
                           fragment_type="analogy")
            ]
        },
        {
            "query": "How does healthcare cost affect families?",
            "fragments": [
                MockFragment("Healthcare costs have risen faster than wages over the past decade"),
                MockFragment("Families allocate larger budget share to medical expenses",
                           fragment_type="impact")
            ]
        },
        {
            "query": "Explain the quantitative mechanism of economic growth",
            "fragments": [
                MockFragment("Economic growth typically slows during periods of high uncertainty"),
                MockFragment("Businesses delay investment decisions until clarity improves",
                           fragment_type="mechanism")
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Scenario {i}: \"{scenario['query']}\" ---")
        
        # Generate 3 variations
        variations = speaker.speak_multiple(
            scenario["query"],
            scenario["fragments"],
            count=3
        )
        
        for j, var in enumerate(variations, 1):
            print(f"  Variation {j}: {var}")
        
        print()
    
    # Show stats
    stats = speaker.get_generation_stats()
    print(f"Session Stats: {stats}")
    
    print("\n=== Demo Complete ===")
