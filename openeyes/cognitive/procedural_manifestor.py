"""
Procedural Linguistic Manifestor for OpenEyes
Generates infinite human-like variations from verified facts using compressed Linguistic DNA
Zero hallucination guaranteed - facts are immutable, only styling varies
"""

import json
import random
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class ProceduralManifestor:
    def __init__(self, dna_file: str = None):
        if dna_file is None:
            dna_file = Path(__file__).parent.parent / "knowledge" / "linguistic_dna.json"
        
        self.dna_file = str(dna_file)
        self.dna = self._load_dna()
        self.used_patterns = set()
        self.session_id = random.randint(1000, 9999)
        
    def _load_dna(self) -> Dict:
        """Load compressed linguistic DNA patterns"""
        try:
            with open(self.dna_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Linguistic DNA file not found: {self.dna_file}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in linguistic DNA: {e}")
    
    def _weighted_choice(self, items: List[Dict], use_text_key: bool = True) -> str:
        """Select item based on weights with anti-repetition logic"""
        if not items:
            return ""
        
        # Check if items have 'text' key or 'pattern' key
        has_text = items and 'text' in items[0]
        has_pattern = items and 'pattern' in items[0]
        
        if not has_text and not has_pattern:
            return ""
        
        # Filter out recently used patterns if possible
        key = 'text' if has_text else 'pattern'
        available = [item for item in items if item[key] not in self.used_patterns]
        if not available:
            available = items  # Fallback if all used
            self.used_patterns.clear()  # Reset if exhausted
        
        # Weighted random selection
        total_weight = sum(item['weight'] for item in available)
        if total_weight == 0:
            return random.choice(available)[key]
        
        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        for item in available:
            cumulative += item['weight']
            if rand_val <= cumulative:
                selected = item[key]
                self.used_patterns.add(selected)
                return selected
        
        return available[-1][key]
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent to select appropriate tone cluster"""
        query_lower = query.lower()
        
        # Urgent concerns
        urgent_keywords = ['emergency', 'urgent', 'critical', 'danger', 'hurt', 'harm', 'stop', 'wrong']
        if any(kw in query_lower for kw in urgent_keywords):
            return 'urgent_concern'
        
        # Technical deep dives
        technical_keywords = ['mechanism', 'quantitative', 'technical', 'formula', 'calculate', 'mathematical', 'empirical']
        if any(kw in query_lower for kw in technical_keywords):
            return 'technical_deep_dive'
        
        # Casual queries
        casual_indicators = ['hey', 'what\'s up', 'tell me about', 'what\'s the deal', 'explain like', 'simple']
        if any(ind in query_lower for ind in casual_indicators):
            return 'casual_query'
        
        # Educational/exploratory
        if '?' in query or any(kw in query_lower for kw in ['how', 'why', 'what', 'when', 'where']):
            return 'educational'
        
        return 'exploratory'
    
    def _get_opening_style(self, intent: str) -> str:
        """Get opening phrase based on intent cluster"""
        clusters = self.dna['clusters']['intent_clusters'].get(intent, ['casual'])
        style_type = random.choice(clusters)
        
        openings = self.dna['clusters']['openings'].get(style_type, self.dna['clusters']['openings']['casual'])
        return self._weighted_choice(openings)
    
    def _get_connector(self, connector_type: str) -> str:
        """Get transitional connector"""
        connectors = self.dna['clusters']['connectors'].get(connector_type, [])
        if not connectors:
            return " "
        return self._weighted_choice(connectors)
    
    def _get_closing(self, intent: str) -> str:
        """Get closing phrase based on intent"""
        if intent == 'technical_deep_dive':
            closings = self.dna['clusters']['closings']['summary']
        elif intent == 'urgent_concern':
            closings = self.dna['clusters']['closings']['action_oriented']
        else:
            closings = self.dna['clusters']['closings']['open_ended']
        
        return self._weighted_choice(closings)
    
    def _get_analogy_intro(self) -> str:
        """Get analogy introduction phrase"""
        return self._weighted_choice(self.dna['clusters']['connectors']['analogy_intro'])
    
    def _build_response(self, 
                       fact: str, 
                       mechanism: Optional[str] = None,
                       impact: Optional[str] = None,
                       analogy: Optional[str] = None,
                       counterpoint: Optional[str] = None,
                       key_point: Optional[str] = None,
                       intent: str = 'casual_query') -> str:
        """Build response using procedural sentence structures"""
        
        # Select sentence structure based on available components
        structures = self.dna['clusters']['sentence_structures']
        available_structures = []
        
        for struct in structures:
            pattern = struct['pattern']
            required = []
            if '{mechanism}' in pattern and mechanism:
                required.append('mechanism')
            if '{impact}' in pattern and impact:
                required.append('impact')
            if '{analogy}' in pattern and analogy:
                required.append('analogy')
            if '{counterpoint}' in pattern and counterpoint:
                required.append('counterpoint')
            if '{key_point}' in pattern and key_point:
                required.append('key_point')
            
            # Check if structure matches available components
            can_use = True
            for req in required:
                if locals().get(req) is None:
                    can_use = False
                    break
            
            if can_use:
                available_structures.append(struct)
        
        if not available_structures:
            # Fallback to simplest structure
            available_structures = [s for s in structures if '{fact}' in s['pattern']]
            if not available_structures:
                return fact
        
        structure = random.choice(available_structures)
        pattern = structure['pattern']
        
        # Build components
        opening = self._get_opening_style(intent)
        closing = self._get_closing(intent)
        
        # Randomly add filler phrases for natural variation
        filler = ""
        if random.random() > 0.6:
            filler_type = random.choice(['thoughtful_pauses', 'confidence_markers', 'hedging_phrases'])
            filler_items = self.dna['clusters']['filler_phrases'].get(filler_type, [])
            if filler_items:
                filler = self._weighted_choice(filler_items)
        
        # Replace placeholders
        response = pattern
        response = response.replace('{opening}', opening)
        response = response.replace('{fact}', fact)
        response = response.replace('{mechanism}', mechanism or '')
        response = response.replace('{impact}', impact or '')
        response = response.replace('{analogy}', analogy or '')
        response = response.replace('{counterpoint}', counterpoint or '')
        response = response.replace('{key_point}', key_point or '')
        
        # Get appropriate connectors based on context
        if mechanism:
            connector = self._get_connector('definition_to_mechanism')
        elif impact:
            connector = self._get_connector('fact_to_impact')
        else:
            connector = self._get_connector('analogy_intro')
        
        response = response.replace('{connector}', connector)
        response = response.replace('{analogy_intro}', self._get_analogy_intro())
        response = response.replace('{filler}', filler)
        response = response.replace('{closing}', closing)
        
        # Clean up any remaining unreplaced placeholders
        import re
        response = re.sub(r'\{[^}]+\}', '', response)
        
        # Clean up multiple spaces and ensure proper punctuation
        response = ' '.join(response.split())
        if not response.endswith(('.', '?', '!')):
            response += '.'
        
        return response
    
    def manifest(self, 
                query: str,
                fact: str,
                mechanism: Optional[str] = None,
                impact: Optional[str] = None,
                analogy: Optional[str] = None,
                **kwargs) -> str:
        """
        Generate human-like response from verified facts
        
        Args:
            query: User's question (used for intent detection)
            fact: Core verified fact (immutable)
            mechanism: How it works (optional)
            impact: Real-world consequences (optional)
            analogy: Metaphorical explanation (optional)
            **kwargs: Additional optional components
        
        Returns:
            Natural language response with infinite variance
        """
        if not fact:
            return "I don't have verified information on that topic."
        
        intent = self._detect_intent(query)
        
        # Extract optional components from kwargs
        counterpoint = kwargs.get('counterpoint')
        key_point = kwargs.get('key_point')
        
        response = self._build_response(
            fact=fact,
            mechanism=mechanism,
            impact=impact,
            analogy=analogy,
            counterpoint=counterpoint,
            key_point=key_point,
            intent=intent
        )
        
        return response
    
    def reset_session(self):
        """Reset pattern usage tracking for new conversation"""
        self.used_patterns.clear()
        self.session_id = random.randint(1000, 9999)


# Demo and testing
if __name__ == "__main__":
    print("=== OpenEyes Procedural Linguistic Manifestor Demo ===\n")
    
    manifestor = ProceduralManifestor()
    
    test_cases = [
        {
            "query": "Hey, what's the deal with inflation?",
            "fact": "Inflation is a sustained increase in the general price level of goods and services",
            "mechanism": "Central banks often raise interest rates to combat inflation",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks"
        },
        {
            "query": "Explain the quantitative mechanism of inflation",
            "fact": "Inflation is measured by the Consumer Price Index tracking basket of goods",
            "mechanism": "Prices are weighted by consumption importance and tracked monthly",
            "impact": "Purchasing power erodes proportionally to the inflation rate"
        },
        {
            "query": "How does inflation hurt everyday people?",
            "fact": "Inflation reduces purchasing power for fixed-income households",
            "impact": "Essential goods become less affordable over time",
            "analogy": "It's like a hidden tax on your savings account"
        },
        {
            "query": "What is inflation?",
            "fact": "Inflation is a sustained increase in the general price level of goods and services",
            "mechanism": "Central banks often raise interest rates to combat inflation",
            "analogy": "Your paycheck stays the same size, but your grocery cart shrinks"
        }
    ]
    
    print("Running multiple iterations to show variance:\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"--- Test Case {i}: \"{case['query']}\" ---")
        for run in range(3):
            manifestor.reset_session()  # Reset for maximum variance
            response = manifestor.manifest(**case)
            print(f"Run {run + 1}: {response}")
        print()
    
    print("=== Demo Complete ===")
