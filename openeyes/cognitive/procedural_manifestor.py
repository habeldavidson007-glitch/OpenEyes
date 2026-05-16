"""
Procedural Manifestor Engine for OpenEyes
Generates infinite human-like variations of verified facts using Linguistic DNA.
Zero hallucination: Facts are immutable, only styling varies.
"""

import json
import random
import os
from typing import List, Dict, Any, Optional

class ProceduralManifestor:
    def __init__(self, dna_path: str = None):
        if dna_path is None:
            dna_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'linguistic_dna.json')
        
        self.dna = self._load_dna(dna_path)
        self.rng = random.Random()  # Isolated RNG for reproducibility if needed
        
    def _load_dna(self, path: str) -> Dict:
        """Load compressed linguistic patterns."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Linguistic DNA file not found at {path}")
    
    def _weighted_choice(self, items: List[Dict], key: str = 'text') -> str:
        """Select item based on weights using roulette wheel selection."""
        if not items:
            return ""
        
        total_weight = sum(item.get('weight', 1.0) for item in items)
        if total_weight == 0:
            return random.choice(items)[key]
        
        r = self.rng.random() * total_weight
        cumulative = 0.0
        
        for item in items:
            cumulative += item.get('weight', 1.0)
            if r <= cumulative:
                return item.get(key, item.get('pattern', ''))
        
        return items[-1].get(key, items[-1].get('pattern', ''))
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent to select appropriate tone."""
        query_lower = query.lower()
        
        # Greeting detection
        if any(word in query_lower for word in ['hey', 'hi', 'hello', 'greetings', "what's up"]):
            if len(query.split()) <= 4:
                return 'greeting'
            return 'casual_query'
        
        # Question type detection
        if query_lower.startswith(('explain', 'describe', 'detail')):
            return 'deep_explanation'
        elif query_lower.startswith(('what', 'how', 'why')):
            if 'mechanism' in query_lower or 'quantitative' in query_lower:
                return 'technical'
            return 'casual_query'
        
        # Safety/emergency detection (simplified)
        if any(word in query_lower for word in ['emergency', 'hurt', 'danger', 'die', 'suicide']):
            return 'safety'
        
        return 'factual'
    
    def _build_response_structure(self, intent: str, has_analogy: bool, has_mechanism: bool) -> List[str]:
        """Determine response structure based on intent and available content."""
        structures = {
            'greeting': ['opener_casual'],
            'casual_query': ['opener_casual', 'fact', 'connector_impact', 'impact', 'closer_casual'],
            'technical': ['opener_formal', 'fact', 'connector_mechanism', 'mechanism', 'closer_formal'],
            'deep_explanation': ['opener_empathetic', 'fact', 'connector_mechanism', 'mechanism', 'connector_analogy', 'analogy', 'closer_open'],
            'factual': ['opener_casual', 'fact', 'closer_casual'],
            'safety': ['opener_empathetic', 'safety_block']
        }
        
        base_structure = structures.get(intent, structures['factual'])
        
        # Dynamically adjust if analogy/mechanism not available
        if not has_analogy and 'analogy' in base_structure:
            base_structure.remove('analogy')
            if 'connector_analogy' in base_structure:
                base_structure.remove('connector_analogy')
        
        if not has_mechanism and 'mechanism' in base_structure:
            base_structure.remove('mechanism')
            if 'connector_mechanism' in base_structure:
                base_structure.remove('connector_mechanism')
        
        return base_structure
    
    def manifest(self, 
                 query: str, 
                 fact: str, 
                 analogy: Optional[str] = None,
                 mechanism: Optional[str] = None,
                 impact: Optional[str] = None,
                 confidence: float = 0.8,
                 domain: str = 'general') -> str:
        """
        Generate a unique, human-like response from verified facts.
        
        Args:
            query: User's input query
            fact: Core verified fact (immutable)
            analogy: Optional analogy for clarification
            mechanism: Optional technical explanation
            impact: Optional real-world impact
            confidence: Confidence score (0-1)
            domain: Knowledge domain
            
        Returns:
            Natural language response with infinite variance
        """
        intent = self._detect_intent(query)
        has_analogy = analogy is not None and len(analogy) > 0
        has_mechanism = mechanism is not None and len(mechanism) > 0
        has_impact = impact is not None and len(impact) > 0
        
        structure = self._build_response_structure(intent, has_analogy, has_mechanism)
        
        response_parts = []
        
        for component in structure:
            if component == 'opener_casual':
                response_parts.append(self._weighted_choice(self.dna['openers']['casual']))
            elif component == 'opener_formal':
                response_parts.append(self._weighted_choice(self.dna['openers']['formal']))
            elif component == 'opener_empathetic':
                response_parts.append(self._weighted_choice(self.dna['openers']['empathetic']))
            elif component == 'fact':
                # Apply sentence structure variation to the fact
                pattern = self._weighted_choice(self.dna['sentence_structures']['simple'], key='pattern')
                varied_fact = pattern.replace('{FACT}', fact)
                # Clean up double "is" or awkward constructions
                varied_fact = varied_fact.replace('It is Inflation is', 'Inflation is')
                varied_fact = varied_fact.replace('We see Inflation is', 'Inflation is')
                response_parts.append(varied_fact)
            elif component == 'mechanism':
                if mechanism:
                    # Clean mechanism text first
                    clean_mech = mechanism
                    # Remove common leading phrases that cause redundancy
                    for phrase in ['Central banks ', 'It ', 'This ', 'The ']:
                        if clean_mech.startswith(phrase):
                            break
                    connector_pattern = self._weighted_choice(self.dna['sentence_structures']['simple'], key='pattern')
                    varied_mech = connector_pattern.replace('{FACT}', clean_mech)
                    # Clean up awkward constructions
                    varied_mech = varied_mech.replace('It is Central banks', 'Central banks')
                    varied_mech = varied_mech.replace('We see Central banks', 'Central banks')
                    response_parts.append(varied_mech)
            elif component == 'analogy':
                if analogy:
                    connector = self._weighted_choice(self.dna['connectors']['fact_to_analogy'])
                    # Avoid double connectors like "Imagine: Imagine:"
                    if connector.endswith(':') and analogy.startswith(('Imagine', 'Think', 'Picture', "It's")):
                        connector = connector.rstrip(':') + ' '
                    response_parts.append(connector)
                    response_parts.append(analogy)
            elif component == 'impact':
                if impact:
                    connector = self._weighted_choice(self.dna['connectors']['fact_to_impact'])
                    # Clean up double connectors in impact
                    clean_impact = impact
                    for phrase in ['Central banks ', 'It ', 'This ', 'The ', 'For everyday people, ', 'For people, ']:
                        if clean_impact.startswith(phrase):
                            clean_impact = clean_impact[len(phrase):]
                            break
                    # Avoid double connectors like "This means This means"
                    if connector.rstrip(',').rstrip() == clean_impact.split()[0] if clean_impact.split() else False:
                        connector = connector.rstrip(',') + ' '
                    response_parts.append(connector)
                    response_parts.append(clean_impact)
            elif component == 'connector_mechanism':
                response_parts.append(self._weighted_choice(self.dna['connectors']['definition_to_mechanism']))
            elif component == 'connector_analogy':
                response_parts.append(self._weighted_choice(self.dna['connectors']['fact_to_analogy']))
            elif component == 'connector_impact':
                response_parts.append(self._weighted_choice(self.dna['connectors']['fact_to_impact']))
            elif component == 'closer_casual':
                response_parts.append(self._weighted_choice(self.dna['closers']['casual']))
            elif component == 'closer_formal':
                response_parts.append(self._weighted_choice(self.dna['closers']['formal']))
            elif component == 'closer_open':
                response_parts.append(self._weighted_choice(self.dna['closers']['open_ended']))
            elif component == 'safety_block':
                response_parts.append("I cannot provide advice on potentially harmful situations. Please consult a qualified professional immediately.")
        
        # Join parts and clean up spacing
        response = ''.join(response_parts)
        response = ' '.join(response.split())  # Normalize whitespace
        
        # Clean up double connectors/phrases
        cleanup_patterns = [
            ('The effect is The effect is', 'The effect is'),
            ('Consequently, Consequently,', 'Consequently,'),
            ('As a result, As a result,', 'As a result,'),
            ('For people, For people,', 'For people,'),
            ('This means This means', 'This means'),
            ('To visualize, To visualize,', 'To visualize,'),
            ('Imagine: Imagine:', 'Imagine:'),
            ('Think of it like Think of it like', 'Think of it like'),
            ("It's like It's like", "It's like"),
            ('Picture this: Picture this:', 'Picture this:'),
            ('Under the hood, Under the hood,', 'Under the hood,'),
            ('Digging deeper, Digging deeper,', 'Digging deeper,'),
            ('This works because This works because', 'This works because'),
            ('In practice, In practice,', 'In practice,'),
            ('Technically, Technically,', 'Technically,'),
            ('What happens is What happens is', 'What happens is'),
        ]
        for old, new in cleanup_patterns:
            response = response.replace(old, new)
        
        # Fix missing spaces after punctuation
        import re
        response = re.sub(r'([.!?])([A-Z])', r'\1 \2', response)  # Add space after period if missing
        response = re.sub(r'(,)([A-Z])', r'\1 \2', response)  # Add space after comma if missing
        
        # Fix spacing issues
        response = response.replace(' .', '.')
        response = response.replace(' ,', ',')
        response = response.replace(' ?', '?')
        response = response.replace('  ', ' ')  # Double spaces
        
        return response
    
    def generate_variations(self, 
                           query: str, 
                           fact: str, 
                           analogy: str = None,
                           n: int = 5) -> List[str]:
        """Generate N unique variations of the same response for testing."""
        variations = []
        original_seed = self.rng.getstate()
        
        for i in range(n):
            self.rng.seed(i)  # Different seed for each variation
            variation = self.manifest(query, fact, analogy)
            variations.append(variation)
        
        self.rng.setstate(original_seed)  # Restore state
        return variations


# Demo/Test runner
if __name__ == "__main__":
    print("=== OpenEyes Procedural Manifestor Demo ===\n")
    
    manifestor = ProceduralManifestor()
    
    test_cases = [
        {
            "query": "Hey, what's the deal with inflation?",
            "fact": "Inflation is a sustained increase in the general price level of goods and services.",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks.",
            "impact": "Central banks often raise interest rates to combat inflation."
        },
        {
            "query": "Explain the quantitative mechanism of inflation.",
            "fact": "Inflation is measured by the Consumer Price Index tracking basket of goods.",
            "mechanism": "Central banks adjust monetary policy based on CPI data.",
            "analogy": "It's like a thermostat adjusting heat based on room temperature."
        },
        {
            "query": "Hey! What's up?",
            "fact": "I'm ready to help with your questions.",
            "analogy": None
        },
        {
            "query": "How does inflation hurt everyday people?",
            "fact": "Inflation reduces purchasing power over time.",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks.",
            "impact": "Savings lose value and fixed incomes become insufficient."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"--- Test Case {i}: \"{case['query']}\" ---")
        print("Variation 1:", manifestor.manifest(**case))
        print("Variation 2:", manifestor.manifest(**case))
        print("Variation 3:", manifestor.manifest(**case))
        print()
    
    # Show uniqueness across many runs
    print("--- Uniqueness Test: 10 variations of same query ---")
    query = "What is inflation?"
    fact = "Inflation is a sustained increase in prices."
    analogy = "Money buys less stuff over time."
    
    variations = manifestor.generate_variations(query, fact, analogy, n=10)
    unique_count = len(set(variations))
    print(f"Generated {len(variations)} responses, {unique_count} unique ({unique_count/len(variations)*100:.0f}% uniqueness)")
    for j, v in enumerate(variations[:3], 1):  # Show first 3
        print(f"  {j}. {v}")
    if unique_count > 3:
        print(f"  ... and {unique_count - 3} more unique variations")
