"""
Calibration Harness for OpenEyes
Validates fragment confidence by domain risk tier and applies acceptance thresholds.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RiskTier(Enum):
    CRITICAL = "critical"  # Healthcare, Governance - highest stakes
    HIGH = "high"          # Economy - financial decisions
    MEDIUM = "medium"      # Science, Philosophy, Social Sciences
    LOW = "low"            # History, Education - lower immediate stakes


@dataclass
class CalibrationResult:
    fragment_id: str
    domain: str
    sector: str
    confidence_score: float
    threshold: float
    passed: bool
    risk_tier: str
    flags: List[str]


class CalibrationHarness:
    """
    Calibrates fragment confidence scores against domain-specific risk thresholds.
    
    Features:
    - Domain/risk tier specific thresholds
    - Confidence scoring based on evidence weights
    - Recency decay adjustment
    - Cross-domain corroboration bonus
    - Contradiction penalty
    """
    
    def __init__(self, domain_rules_path: str = "domain_rules"):
        self.domain_rules_path = domain_rules_path
        self.domain_configs = self._load_domain_configs()
        
    def _load_domain_configs(self) -> Dict:
        """Load all domain configuration files."""
        configs = {}
        if not os.path.exists(self.domain_rules_path):
            return configs
            
        for filename in os.listdir(self.domain_rules_path):
            if filename.endswith('.json') and filename != '__init__.py':
                filepath = os.path.join(self.domain_rules_path, filename)
                with open(filepath, 'r') as f:
                    config = json.load(f)
                    domain_code = config.get('code', '').lower()
                    if domain_code:
                        configs[domain_code] = config
        return configs
    
    def get_risk_tier(self, domain_code: str) -> RiskTier:
        """Get risk tier for a domain."""
        config = self.domain_configs.get(domain_code.lower(), {})
        tier_str = config.get('risk_tier', 'medium')
        try:
            return RiskTier(tier_str)
        except ValueError:
            return RiskTier.MEDIUM
    
    def get_threshold(self, domain_code: str) -> float:
        """Get calibration threshold for a domain."""
        config = self.domain_configs.get(domain_code.lower(), {})
        return config.get('calibration_threshold', 0.75)
    
    def calculate_confidence_score(
        self,
        fragment: Dict,
        domain_code: str,
        cross_domain_corroboration: float = 0.0,
        contradiction_score: float = 0.0
    ) -> float:
        """
        Calculate confidence score for a fragment.
        
        Args:
            fragment: Fragment JSON data
            domain_code: Domain code (eco, hc, gov, etc.)
            cross_domain_corroboration: Score from cross-domain verification (0-1)
            contradiction_score: Score of contradictions found (0-1, higher = more contradictory)
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        config = self.domain_configs.get(domain_code.lower(), {})
        rules = config.get('fragment_rules', {})
        weights = rules.get('evidence_indexing_weights', {
            'source_credibility': 0.4,
            'recency': 0.3,
            'peer_reviewed': 0.2,
            'cross_domain_corroboration': 0.1
        })
        
        # Source credibility score (based on primary source match)
        source_score = self._calculate_source_credibility(fragment, config)
        
        # Recency score (decay based on age)
        recency_score = self._calculate_recency_score(fragment, rules)
        
        # Peer-reviewed bonus
        peer_reviewed_score = self._check_peer_reviewed(fragment)
        
        # Cross-domain corroboration bonus
        corroboration_bonus = cross_domain_corroboration * weights.get('cross_domain_corroboration', 0.1)
        
        # Contradiction penalty
        contradiction_penalty = contradiction_score * 0.3  # Max 30% penalty
        
        # Weighted sum
        confidence = (
            source_score * weights.get('source_credibility', 0.4) +
            recency_score * weights.get('recency', 0.3) +
            peer_reviewed_score * weights.get('peer_reviewed', 0.2) +
            corroboration_bonus -
            contradiction_penalty
        )
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def _calculate_source_credibility(self, fragment: Dict, config: Dict) -> float:
        """Calculate source credibility score (0-1)."""
        primary_sources = config.get('primary_sources', [])
        source_url = fragment.get('source_url', '')
        source_name = fragment.get('source', '')
        
        # Check if source matches primary sources
        for primary in primary_sources:
            if primary.lower() in source_url.lower() or primary.lower() in source_name.lower():
                return 1.0
        
        # Check for academic/government domains
        credible_domains = ['.gov', '.edu', '.org', 'pubmed', 'arxiv', 'nature.com', 'science.org']
        for domain in credible_domains:
            if domain in source_url.lower():
                return 0.8
        
        # Unknown source
        return 0.5
    
    def _calculate_recency_score(self, fragment: Dict, rules: Dict) -> float:
        """Calculate recency score with decay (0-1)."""
        year = fragment.get('year')
        if not year:
            return 0.5  # Neutral if unknown
        
        from datetime import datetime
        current_year = datetime.now().year
        age = current_year - int(year)
        recency_cap = rules.get('recency_cap_years', 5)
        
        if age <= 0:
            return 1.0
        elif age <= recency_cap:
            # Linear decay within cap
            return 1.0 - (age / recency_cap) * 0.3
        else:
            # Exponential decay beyond cap
            return max(0.2, 0.7 * (0.9 ** (age - recency_cap)))
    
    def _check_peer_reviewed(self, fragment: Dict) -> float:
        """Check if source is peer-reviewed."""
        source_url = fragment.get('source_url', '').lower()
        source_name = fragment.get('source', '').lower()
        
        peer_reviewed_indicators = [
            'pubmed', 'arxiv', 'nature', 'science', 'ieee', 'doi',
            'journal', 'peer-reviewed', 'academic', 'university'
        ]
        
        for indicator in peer_reviewed_indicators:
            if indicator in source_url or indicator in source_name:
                return 1.0
        
        return 0.5  # Unknown
    
    def validate_fragment(
        self,
        fragment: Dict,
        domain_code: str,
        cross_domain_corroboration: float = 0.0,
        contradiction_score: float = 0.0
    ) -> CalibrationResult:
        """
        Validate a fragment against domain threshold.
        
        Returns:
            CalibrationResult with pass/fail status
        """
        confidence = self.calculate_confidence_score(
            fragment, domain_code, cross_domain_corroboration, contradiction_score
        )
        threshold = self.get_threshold(domain_code)
        risk_tier = self.get_risk_tier(domain_code)
        
        flags = []
        if confidence < threshold:
            flags.append("below_threshold")
        if contradiction_score > 0.5:
            flags.append("high_contradiction")
        if fragment.get('year') and int(fragment['year']) < 2000:
            flags.append("outdated")
        
        return CalibrationResult(
            fragment_id=fragment.get('id', 'unknown'),
            domain=domain_code,
            sector=fragment.get('sector', 'unknown'),
            confidence_score=confidence,
            threshold=threshold,
            passed=confidence >= threshold,
            risk_tier=risk_tier.value,
            flags=flags
        )
    
    def validate_batch(
        self,
        fragments: List[Dict],
        domain_code: str
    ) -> Tuple[int, int, List[CalibrationResult]]:
        """
        Validate a batch of fragments.
        
        Returns:
            Tuple of (passed_count, failed_count, results_list)
        """
        results = []
        passed = 0
        failed = 0
        
        for fragment in fragments:
            result = self.validate_fragment(fragment, domain_code)
            results.append(result)
            if result.passed:
                passed += 1
            else:
                failed += 1
        
        return passed, failed, results
    
    def get_domain_statistics(self, domain_code: str) -> Dict:
        """Get calibration statistics for a domain."""
        config = self.domain_configs.get(domain_code.lower(), {})
        return {
            'domain': config.get('domain', domain_code),
            'risk_tier': config.get('risk_tier', 'medium'),
            'calibration_threshold': config.get('calibration_threshold', 0.75),
            'total_sectors': len(config.get('sectors', [])),
            'fragment_rules': config.get('fragment_rules', {})
        }


# Convenience function for quick validation
def calibrate_fragment(fragment: Dict, domain_code: str) -> CalibrationResult:
    """Quick single-fragment calibration."""
    harness = CalibrationHarness()
    return harness.validate_fragment(fragment, domain_code)


if __name__ == "__main__":
    # Test the calibration harness
    harness = CalibrationHarness()
    
    print("OpenEyes Calibration Harness")
    print("=" * 50)
    
    for domain_code in ['hc', 'gov', 'eco', 'sat', 'his', 'phi', 'soc', 'edu']:
        stats = harness.get_domain_statistics(domain_code)
        print(f"\n{stats['domain']} ({domain_code.upper()}):")
        print(f"  Risk Tier: {stats['risk_tier']}")
        print(f"  Threshold: {stats['calibration_threshold']}")
        print(f"  Sectors: {stats['total_sectors']}")
