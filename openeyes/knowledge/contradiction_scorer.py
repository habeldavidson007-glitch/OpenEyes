"""
Contradiction & Counter-Argument Scoring Engine
Detects and scores contradictions between fragments across domains and sectors.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import re


@dataclass
class ContradictionMatch:
    fragment_a_id: str
    fragment_b_id: str
    contradiction_score: float  # 0.0 (no contradiction) to 1.0 (strong contradiction)
    reasoning: str
    domains_involved: List[str]
    sectors_involved: List[str]


class ContradictionScorer:
    """
    Detects and scores contradictions between fragments.
    
    Features:
    - Semantic similarity detection for opposing claims
    - Cross-domain contradiction tracking
    - Counter-argument role analysis
    - Confidence-weighted scoring
    """
    
    def __init__(self, domains_path: str = "domains"):
        self.domains_path = domains_path
        self.contradiction_indicators = [
            "however", "contrary", "opposes", "disputes", "challenges",
            "criticizes", "refutes", "counters", "nevertheless", "on the other hand",
            "in contrast", "conversely", "alternatively", "despite", "although"
        ]
        
        self.negation_patterns = [
            r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bneither\b",
            r"\bwithout\b", r"\bfails?\b", r"\bimpossible\b"
        ]
    
    def load_counter_arguments(self, domain_code: str, sector_code: str) -> List[Dict]:
        """Load counter_argument fragments from a specific sector."""
        counter_args = []
        sector_path = os.path.join(self.domains_path, domain_code, sector_code.lower())
        
        if not os.path.exists(sector_path):
            return counter_args
        
        for filename in os.listdir(sector_path):
            if filename.endswith('.json'):
                filepath = os.path.join(sector_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        fragment = json.load(f)
                        if 'counter_argument' in fragment:
                            fragment['_source_file'] = filename
                            counter_args.append(fragment)
                except (json.JSONDecodeError, IOError):
                    continue
        
        return counter_args
    
    def calculate_textual_contradiction(self, text_a: str, text_b: str) -> float:
        """
        Calculate contradiction score based on textual analysis.
        
        Higher score = more likely to be contradictory
        """
        text_a_lower = text_a.lower()
        text_b_lower = text_b.lower()
        
        # Check for contradiction indicators in text_b about text_a's topic
        has_contradiction_indicator = any(
            indicator in text_b_lower for indicator in self.contradiction_indicators
        )
        
        # Check for negation patterns
        has_negation = any(
            re.search(pattern, text_b_lower) for pattern in self.negation_patterns
        )
        
        # Semantic similarity (high similarity + negation = contradiction)
        similarity = SequenceMatcher(None, text_a_lower, text_b_lower).ratio()
        
        # Topic overlap (extract key terms)
        words_a = set(re.findall(r'\b[a-z]{4,}\b', text_a_lower))
        words_b = set(re.findall(r'\b[a-z]{4,}\b', text_b_lower))
        topic_overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
        
        # Score calculation
        base_score = 0.0
        
        if has_contradiction_indicator:
            base_score += 0.3
        
        if has_negation and topic_overlap > 0.3:
            base_score += 0.4
        
        # High similarity + some negation = strong contradiction
        if similarity > 0.6 and (has_negation or has_contradiction_indicator):
            base_score += 0.3
        
        # Topic overlap boosts confidence
        base_score *= (1.0 + min(topic_overlap, 0.5))
        
        return min(1.0, base_score)
    
    def detect_cross_sector_contradictions(
        self,
        fragment: Dict,
        target_domains: Optional[List[str]] = None
    ) -> List[ContradictionMatch]:
        """
        Detect contradictions for a fragment across sectors/domains.
        
        Args:
            fragment: The fragment to check
            target_domains: List of domain codes to search (None = all)
        
        Returns:
            List of ContradictionMatch objects
        """
        contradictions = []
        
        definition = fragment.get('definition', '')
        if not definition:
            return contradictions
        
        source_domain = fragment.get('domain', '').lower()
        source_sector = fragment.get('sector', '').lower()
        
        # Load cross-domain relationships to prioritize searches
        relationships = self._load_relationships()
        related_sectors = self._get_related_sectors(
            source_domain, source_sector, relationships
        )
        
        # Search in related sectors first, then others
        search_order = related_sectors + self._get_all_other_sectors(source_domain, source_sector)
        
        checked_count = 0
        max_checks = 50  # Limit to prevent excessive computation
        
        for domain_code, sector_code in search_order:
            if target_domains and domain_code not in target_domains:
                continue
            
            if checked_count >= max_checks:
                break
            
            counter_args = self.load_counter_arguments(domain_code, sector_code)
            
            for counter_frag in counter_args:
                counter_text = counter_frag.get('counter_argument', '')
                if not counter_text:
                    continue
                
                score = self.calculate_textual_contradiction(definition, counter_text)
                
                if score > 0.4:  # Threshold for reporting
                    match = ContradictionMatch(
                        fragment_a_id=fragment.get('id', 'unknown'),
                        fragment_b_id=counter_frag.get('id', 'unknown'),
                        contradiction_score=score,
                        reasoning=self._generate_reasoning(score, counter_text),
                        domains_involved=[source_domain, domain_code],
                        sectors_involved=[source_sector, sector_code]
                    )
                    contradictions.append(match)
                    checked_count += 1
        
        # Sort by score descending
        contradictions.sort(key=lambda x: x.contradiction_score, reverse=True)
        return contradictions[:10]  # Return top 10
    
    def _load_relationships(self) -> Dict:
        """Load cross-domain relationship configuration."""
        rel_path = os.path.join("data", "cross_domain_relationships.json")
        if os.path.exists(rel_path):
            with open(rel_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _get_related_sectors(
        self,
        domain: str,
        sector: str,
        relationships: Dict
    ) -> List[Tuple[str, str]]:
        """Get sectors related to this domain/sector pair."""
        related = []
        
        for rel in relationships.get('relationships', []):
            if rel['domain_a'] == domain and rel['sector_a'] == sector:
                related.append((rel['domain_b'], rel['sector_b']))
            elif rel['domain_b'] == domain and rel['sector_b'] == sector:
                related.append((rel['domain_a'], rel['sector_a']))
        
        return related
    
    def _get_all_other_sectors(self, exclude_domain: str, exclude_sector: str) -> List[Tuple[str, str]]:
        """Get all sectors except the specified one."""
        all_sectors = []
        
        if not os.path.exists(self.domains_path):
            return all_sectors
        
        for domain_code in os.listdir(self.domains_path):
            domain_path = os.path.join(self.domains_path, domain_code)
            if not os.path.isdir(domain_path):
                continue
            
            for sector_code in os.listdir(domain_path):
                sector_path = os.path.join(domain_path, sector_code)
                if os.path.isdir(sector_path):
                    if domain_code != exclude_domain or sector_code != exclude_sector:
                        all_sectors.append((domain_code, sector_code))
        
        return all_sectors
    
    def _generate_reasoning(self, score: float, counter_text: str) -> str:
        """Generate human-readable reasoning for contradiction score."""
        if score > 0.8:
            return "Strong contradiction detected with direct opposing claims"
        elif score > 0.6:
            return "Moderate contradiction with significant claim opposition"
        elif score > 0.4:
            return "Weak contradiction with some opposing elements"
        else:
            return "Minimal contradiction detected"
    
    def get_fragment_contradiction_summary(self, fragment: Dict) -> Dict:
        """
        Get a summary of contradictions for a fragment.
        
        Returns:
            Dictionary with contradiction statistics
        """
        contradictions = self.detect_cross_sector_contradictions(fragment)
        
        if not contradictions:
            return {
                'fragment_id': fragment.get('id', 'unknown'),
                'total_contradictions': 0,
                'max_score': 0.0,
                'avg_score': 0.0,
                'domains_in_conflict': [],
                'status': 'no_contradictions'
            }
        
        scores = [c.contradiction_score for c in contradictions]
        domains = set()
        for c in contradictions:
            domains.update(c.domains_involved)
        
        return {
            'fragment_id': fragment.get('id', 'unknown'),
            'total_contradictions': len(contradictions),
            'max_score': max(scores),
            'avg_score': sum(scores) / len(scores),
            'domains_in_conflict': list(domains),
            'top_contradictions': [
                {
                    'with_fragment': c.fragment_b_id,
                    'score': c.contradiction_score,
                    'reasoning': c.reasoning
                }
                for c in contradictions[:3]
            ],
            'status': 'high_conflict' if max(scores) > 0.7 else 'moderate_conflict' if max(scores) > 0.5 else 'low_conflict'
        }


# Convenience function
def score_contradictions(fragment: Dict) -> Dict:
    """Quick contradiction scoring for a single fragment."""
    scorer = ContradictionScorer()
    return scorer.get_fragment_contradiction_summary(fragment)


if __name__ == "__main__":
    print("OpenEyes Contradiction Scorer")
    print("=" * 50)
    
    # Test with a sample fragment
    scorer = ContradictionScorer()
    
    # Example test
    test_fragment = {
        'id': 'test_001',
        'domain': 'eco',
        'sector': 'mac',
        'definition': 'Inflation is primarily caused by excessive money supply growth.',
        'counter_argument': 'Some economists argue inflation is driven by supply shocks.'
    }
    
    result = scorer.get_fragment_contradiction_summary(test_fragment)
    print(f"\nTest Fragment: {result['fragment_id']}")
    print(f"Contradictions Found: {result['total_contradictions']}")
    print(f"Status: {result['status']}")
