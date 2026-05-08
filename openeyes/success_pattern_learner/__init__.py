"""
Success Pattern Learner - Adaptive Fallback System

Learns from successful query outcomes to enable intelligent fallbacks.
Instead of rigidly halting when requirements aren't met, the system
checks historical success patterns for similar queries and dynamically
adjusts requirements.

Key Features:
- Observes successful queries and extracts patterns (domain, tier, fragment roles)
- Stores patterns in persistent JSON cache
- Enables adaptive tier downgrade when similar low-risk queries succeeded
- Maintains safety while improving responsiveness
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class SuccessPatternLearner:
    """Learns and applies success patterns for adaptive fallbacks."""
    
    def __init__(self, cache_path: str = "/workspace/logs/success_patterns.json"):
        self.cache_path = Path(cache_path)
        self.patterns: List[Dict[str, Any]] = []
        self.load_patterns()
    
    def load_patterns(self):
        """Load patterns from persistent cache."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)
                    self.patterns = data.get('patterns', [])
            except Exception as e:
                print(f"[PatternLearner] Error loading patterns: {e}")
                self.patterns = []
        else:
            self.patterns = []
    
    def save_patterns(self):
        """Save patterns to persistent cache."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'pattern_count': len(self.patterns),
                'patterns': self.patterns
            }, f, indent=2)
    
    def observe_success(self, query: str, domain: str, tier: str, 
                       fragments: List[Dict[str, Any]], confidence: float):
        """
        Record a successful query outcome as a learning pattern.
        
        Args:
            query: Original query text (will be normalized)
            domain: Domain name (medical, engineering, cooking, etc.)
            tier: Tier level (tier1, tier2, tier3)
            fragments: List of fragments that succeeded
            confidence: Final confidence score
        """
        # Extract pattern features
        fragment_roles = [f.get('reasoning_role', 'unknown') for f in fragments]
        has_definition = 'definition' in fragment_roles
        has_counter = 'counter_argument' in fragment_roles
        has_latest = 'latest_data' in fragment_roles
        num_fragments = len(fragments)
        num_sources = len(set(f.get('source', '') for f in fragments))
        
        # Create pattern signature
        pattern = {
            'query_hash': hashlib.md5(query.lower().encode()).hexdigest()[:8],
            'domain': domain,
            'tier': tier,
            'has_definition': has_definition,
            'has_counter': has_counter,
            'has_latest': has_latest,
            'fragment_roles': fragment_roles,
            'num_fragments': num_fragments,
            'num_sources': num_sources,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        
        self.patterns.append(pattern)
        
        # Keep only last 500 patterns to prevent unbounded growth
        if len(self.patterns) > 500:
            self.patterns = self.patterns[-500:]
        
        self.save_patterns()
        print(f"[PatternLearner] Recorded success pattern: {domain}/{tier} with {num_fragments} fragments")
    
    def check_fallback_permission(self, query: str, domain: str, tier: str,
                                  missing_requirements: List[str]) -> Dict[str, Any]:
        """
        Check if historical patterns permit a fallback despite missing requirements.
        
        Args:
            query: Current query text
            domain: Domain name
            tier: Current tier requirement
            missing_requirements: List of missing items (e.g., ['counter_argument'])
        
        Returns:
            Dict with 'allow_fallback', 'suggested_tier', 'confidence', 'reason'
        """
        if not missing_requirements:
            return {'allow_fallback': False, 'reason': 'No missing requirements'}
        
        if not self.patterns:
            return {'allow_fallback': False, 'reason': 'No historical patterns available'}
        
        # Find similar successful patterns
        similar_patterns = []
        for pattern in self.patterns:
            if pattern['domain'] != domain:
                continue
            if not pattern['success']:
                continue
            
            # Check if pattern succeeded despite similar gaps
            has_gap = False
            if 'counter_argument' in missing_requirements and not pattern['has_counter']:
                has_gap = True
            if 'definition' in missing_requirements and not pattern['has_definition']:
                has_gap = True
            if 'latest_data' in missing_requirements and not pattern['has_latest']:
                has_gap = True
            
            if has_gap:
                similar_patterns.append(pattern)
        
        if not similar_patterns:
            return {'allow_fallback': False, 'reason': 'No similar successful patterns with gaps found'}
        
        # Analyze patterns
        avg_confidence = sum(p['confidence'] for p in similar_patterns) / len(similar_patterns)
        high_confidence_count = sum(1 for p in similar_patterns if p['confidence'] >= 70)
        
        # Decision logic
        if len(similar_patterns) >= 3 and high_confidence_count >= 2:
            # Strong evidence for fallback
            suggested_tier = 'tier3' if tier == 'tier1' else ('tier3' if tier == 'tier2' else 'tier3')
            return {
                'allow_fallback': True,
                'suggested_tier': suggested_tier,
                'confidence': avg_confidence,
                'reason': f"Found {len(similar_patterns)} similar successful queries with same gaps (avg confidence: {avg_confidence:.1f}%)",
                'supporting_patterns': len(similar_patterns)
            }
        elif len(similar_patterns) >= 1 and avg_confidence >= 65:
            # Weak evidence - allow with caution
            return {
                'allow_fallback': True,
                'suggested_tier': tier,  # Keep same tier but proceed
                'confidence': avg_confidence * 0.9,  # Slight penalty
                'reason': f"Limited evidence ({len(similar_patterns)} patterns) suggests fallback may be safe",
                'supporting_patterns': len(similar_patterns)
            }
        else:
            return {
                'allow_fallback': False,
                'reason': f"Insufficient evidence ({len(similar_patterns)} patterns, avg confidence {avg_confidence:.1f}%)"
            }
    
    def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a specific domain."""
        domain_patterns = [p for p in self.patterns if p['domain'] == domain]
        
        if not domain_patterns:
            return {'count': 0}
        
        return {
            'count': len(domain_patterns),
            'avg_confidence': sum(p['confidence'] for p in domain_patterns) / len(domain_patterns),
            'avg_fragments': sum(p['num_fragments'] for p in domain_patterns) / len(domain_patterns),
            'with_counter_pct': sum(1 for p in domain_patterns if p['has_counter']) / len(domain_patterns) * 100,
            'high_confidence_pct': sum(1 for p in domain_patterns if p['confidence'] >= 75) / len(domain_patterns) * 100
        }


# Global instance
_pattern_learner = None

def get_pattern_learner() -> SuccessPatternLearner:
    """Get or create global pattern learner instance."""
    global _pattern_learner
    if _pattern_learner is None:
        _pattern_learner = SuccessPatternLearner()
    return _pattern_learner


def record_success(query: str, domain: str, tier: str, 
                   fragments: List[Dict[str, Any]], confidence: float):
    """Convenience function to record a success."""
    learner = get_pattern_learner()
    learner.observe_success(query, domain, tier, fragments, confidence)


def check_fallback(query: str, domain: str, tier: str, 
                   missing: List[str]) -> Dict[str, Any]:
    """Convenience function to check fallback permission."""
    learner = get_pattern_learner()
    return learner.check_fallback_permission(query, domain, tier, missing)
