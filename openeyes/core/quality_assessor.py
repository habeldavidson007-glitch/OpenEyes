"""
Knowledge Quality Assessor for OpenEyes
Consolidates fragment validation, source credibility scoring, and metrics collection.
Replaces separate scoring and validation modules with a unified quality engine.
"""

import time
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class CredibilityLevel(Enum):
    HIGH = "HIGH"       # Peer-reviewed, gov, major institutions
    MEDIUM = "MEDIUM"   # Reputable news, established orgs
    LOW = "LOW"         # Blogs, unknown sources
    UNVERIFIED = "UNVERIFIED" # No source or suspicious

@dataclass
class SourceCredibilityReport:
    url: str
    credibility_level: CredibilityLevel
    score: float  # 0.0 to 1.0
    factors: List[str]
    last_verified: float = field(default_factory=time.time)

@dataclass
class QualityMetrics:
    total_fragments_processed: int = 0
    high_credibility_count: int = 0
    medium_credibility_count: int = 0
    low_credibility_count: int = 0
    hallucination_attempts_blocked: int = 0
    average_confidence: float = 0.0
    domain_breakdown: Dict[str, int] = field(default_factory=dict)

class KnowledgeQualityAssessor:
    """
    Unified engine for assessing knowledge quality, source credibility, 
    and maintaining validation metrics.
    """
    
    def __init__(self):
        self.metrics = QualityMetrics()
        # Trusted domain patterns for credibility scoring
        self.trusted_patterns = [
            ".gov", ".edu", "who.int", "nih.gov", "cdc.gov", 
            "worldbank.org", "imf.org", "nature.com", "science.org",
            "reuters.com", "bloomberg.com", "ft.com"
        ]
        self.suspicious_patterns = [
            "blogspot", "wordpress.com", "medium.com", "reddit.com"
        ]
        
    def assess_source_credibility(self, source_url: str) -> SourceCredibilityReport:
        """
        Evaluate the credibility of a source URL based on domain patterns and history.
        """
        factors = []
        base_score = 0.5
        level = CredibilityLevel.UNVERIFIED
        
        if not source_url or source_url.startswith("internal://"):
            factors.append("Internal or missing source")
            return SourceCredibilityReport(
                url=source_url or "unknown",
                credibility_level=CredibilityLevel.UNVERIFIED,
                score=0.3,
                factors=factors
            )
        
        url_lower = source_url.lower()
        
        # Check trusted patterns
        for pattern in self.trusted_patterns:
            if pattern in url_lower:
                base_score = 0.95
                level = CredibilityLevel.HIGH
                factors.append(f"Trusted domain pattern: {pattern}")
                break
        
        # Check suspicious patterns (if not already high trust)
        if level != CredibilityLevel.HIGH:
            for pattern in self.suspicious_patterns:
                if pattern in url_lower:
                    base_score = 0.4
                    level = CredibilityLevel.LOW
                    factors.append(f"Suspicious/Uncurated platform: {pattern}")
                    break
            
            # Default assessment if no patterns matched
            if not factors:
                if any(ext in url_lower for ext in [".org", ".com"]):
                    base_score = 0.7
                    level = CredibilityLevel.MEDIUM
                    factors.append("Standard commercial/organization domain")
                else:
                    base_score = 0.5
                    level = CredibilityLevel.LOW
                    factors.append("Unknown domain type")
        
        self.metrics.total_fragments_processed += 1
        if level == CredibilityLevel.HIGH:
            self.metrics.high_credibility_count += 1
        elif level == CredibilityLevel.MEDIUM:
            self.metrics.medium_credibility_count += 1
        else:
            self.metrics.low_credibility_count += 1
            
        return SourceCredibilityReport(
            url=source_url,
            credibility_level=level,
            score=base_score,
            factors=factors
        )
    
    def validate_fragment_integrity(self, content: str, source_url: str, timestamp: float) -> Dict[str, Any]:
        """
        Comprehensive integrity check: hallucination, recency, and source fabrication.
        """
        issues = []
        is_valid = True
        
        # 1. Source Fabrication Check
        if not source_url or source_url == "unknown":
            issues.append("MISSING_SOURCE")
            is_valid = False
            self.metrics.hallucination_attempts_blocked += 1
        
        # 2. Recency Check (example: flag if older than 2 years for fast-moving domains)
        current_time = time.time()
        age_days = (current_time - timestamp) / 86400
        if age_days > 730: # 2 years
            issues.append("STALE_DATA")
            # Not necessarily invalid, but flagged
        
        # 3. Content Hallucination Heuristics (simplified)
        if len(content) < 10:
            issues.append("CONTENT_TOO_SHORT")
            is_valid = False
            
        if "I don't know" in content or "no information" in content.lower():
            # This is honest uncertainty, not hallucination, but low utility
            issues.append("LOW_UTILITY_UNCERTAINTY")
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "content_hash": hashlib.md5(content.encode()).hexdigest(),
            "age_days": round(age_days, 2)
        }
    
    def calculate_weighted_confidence(self, base_confidence: float, credibility_score: float, integrity_issues: List[str]) -> float:
        """
        Combine base model confidence with source credibility and integrity checks.
        """
        penalty = 0.0
        for issue in integrity_issues:
            if issue == "MISSING_SOURCE":
                penalty += 0.5
            elif issue == "STALE_DATA":
                penalty += 0.1
            elif issue == "CONTENT_TOO_SHORT":
                penalty += 0.3
        
        # Weighted formula: 60% Base, 40% Credibility, minus penalties
        raw_score = (base_confidence * 0.6) + (credibility_score * 0.4) - penalty
        return max(0.0, min(1.0, raw_score))
    
    def record_domain_usage(self, domain: str):
        """Track usage per domain for metrics."""
        if domain not in self.metrics.domain_breakdown:
            self.metrics.domain_breakdown[domain] = 0
        self.metrics.domain_breakdown[domain] += 1
    
    def get_metrics_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate data for the Validation Metrics Dashboard.
        """
        total = self.metrics.total_fragments_processed
        if total == 0:
            avg_conf = 0.0
        else:
            # Simplified average calculation for demo
            avg_conf = (
                (self.metrics.high_credibility_count * 0.95) +
                (self.metrics.medium_credibility_count * 0.7) +
                (self.metrics.low_credibility_count * 0.4)
            ) / total
            
        return {
            "total_fragments": total,
            "credibility_distribution": {
                "high": self.metrics.high_credibility_count,
                "medium": self.metrics.medium_credibility_count,
                "low": self.metrics.low_credibility_count
            },
            "hallucinations_blocked": self.metrics.hallucination_attempts_blocked,
            "average_quality_score": round(avg_conf, 3),
            "domain_activity": self.metrics.domain_breakdown,
            "timestamp": time.time()
        }

# Singleton instance
assessor = KnowledgeQualityAssessor()
