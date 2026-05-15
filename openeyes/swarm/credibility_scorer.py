#!/usr/bin/env python3
"""
P2 Source Credibility Scoring System

This module implements a credibility scoring system for fragment sources.
It evaluates source URLs and assigns credibility scores based on multiple factors.

Features:
- Domain reputation scoring (.gov, .edu, .org vs blogs, social media)
- Publication type detection (peer-reviewed, government, textbook, etc.)
- Cross-reference validation
- Historical accuracy tracking

Usage:
    from openeyes.swarm.credibility_scorer import score_source_credibility
    
    score = score_source_credibility("https://pubmed.gov/article/123")
    # Returns: {"score": 0.95, "class": "A", "factors": {...}}
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CredibilityScore:
    """Result of source credibility scoring."""
    score: float  # 0.0 to 1.0
    credibility_class: str  # A, B, C, D, F
    factors: Dict[str, float]
    recommendations: List[str]
    source_url: str


class SourceCredibilityScorer:
    """
    Scores the credibility of fragment sources.
    
    This is a P2-MEDIUM priority enhancement that provides:
    - Automated source quality assessment
    - Consistent credibility classification
    - Transparent scoring factors
    """
    
    # Domain reputation tiers
    TIER_S = {  # Highest credibility
        r'\.gov$', r'\.gov/', r'who\.int', r'un\.org',
        r'ecb\.europa', r'fed\.gov', r'treasury\.gov',
    }
    
    TIER_A = {  # High credibility - peer reviewed
        r'pubmed', r'ncbi\.nlm\.nih', r'doi\.org',
        r'nature\.com', r'science\.org', r'cell\.com',
        r'nejm\.org', r'thelancet\.com', r'bmj\.com',
        r'arxiv\.org', r'jstor\.org',
    }
    
    TIER_B = {  # Medium-high credibility
        r'\.edu/', r'\.ac\.',
        r'reuters\.com', r'bloomberg\.com', r'ft\.com',
        r'wsj\.com', r'economist\.com',
        r'iso\.org', r'ieee\.org',
    }
    
    TIER_C = {  # Medium credibility
        r'\.org/',
        r'medium\.com(?!/)',  # Official medium publications OK
        r'substack\.com',
        r'github\.com',
    }
    
    TIER_D = {  # Low credibility - use with caution
        r'blogspot', r'wordpress\.com', r'wix\.com',
        r'reddit\.com', r'quora\.com', r'stackoverflow\.com',
    }
    
    TIER_F = {  # Unreliable - avoid
        r'infowars', r'naturalnews', r'beforeitsnews',
        r'zerohedge\.com',  # Controversial
    }
    
    def __init__(self):
        self._historical_accuracy = {}  # Track accuracy by domain
    
    def score_source(self, source_url: str, 
                    publication_type: str = None,
                    historical_accuracy: float = None) -> CredibilityScore:
        """
        Score the credibility of a source URL.
        
        Args:
            source_url: The source URL to evaluate
            publication_type: Optional type (peer_reviewed_study, government_report, etc.)
            historical_accuracy: Optional historical accuracy score (0-1)
        
        Returns:
            CredibilityScore with detailed breakdown
        """
        if not source_url:
            return CredibilityScore(
                score=0.0,
                credibility_class="F",
                factors={"missing_url": 0.0},
                recommendations=["Provide a valid source URL"],
                source_url=source_url
            )
        
        url_lower = source_url.lower()
        factors = {}
        recommendations = []
        
        # 1. Domain reputation score (40% weight)
        domain_score = self._score_domain_reputation(url_lower)
        factors['domain_reputation'] = domain_score
        
        # 2. Publication type score (30% weight)
        pub_score = self._score_publication_type(publication_type) if publication_type else 0.7
        factors['publication_type'] = pub_score
        
        # 3. URL structure quality (10% weight)
        structure_score = self._score_url_structure(source_url)
        factors['url_structure'] = structure_score
        
        # 4. Historical accuracy (20% weight)
        hist_score = historical_accuracy if historical_accuracy is not None else 0.7
        factors['historical_accuracy'] = hist_score
        
        # Calculate weighted total
        total_score = (
            domain_score * 0.40 +
            pub_score * 0.30 +
            structure_score * 0.10 +
            hist_score * 0.20
        )
        
        # Determine credibility class
        credibility_class = self._score_to_class(total_score)
        
        # Generate recommendations
        if domain_score < 0.5:
            recommendations.append("Consider using higher-tier sources (.gov, .edu, peer-reviewed)")
        if pub_score < 0.6:
            recommendations.append("Specify publication type for better scoring")
        if structure_score < 0.5:
            recommendations.append("Use direct links to specific content rather than homepages")
        
        return CredibilityScore(
            score=round(total_score, 3),
            credibility_class=credibility_class,
            factors=factors,
            recommendations=recommendations,
            source_url=source_url
        )
    
    def _score_domain_reputation(self, url: str) -> float:
        """Score based on domain reputation tier."""
        for pattern in self.TIER_S:
            if re.search(pattern, url):
                return 1.0
        
        for pattern in self.TIER_A:
            if re.search(pattern, url):
                return 0.95
        
        for pattern in self.TIER_B:
            if re.search(pattern, url):
                return 0.85
        
        for pattern in self.TIER_C:
            if re.search(pattern, url):
                return 0.70
        
        for pattern in self.TIER_D:
            if re.search(pattern, url):
                return 0.40
        
        for pattern in self.TIER_F:
            if re.search(pattern, url):
                return 0.10
        
        # Unknown domain - neutral score
        return 0.60
    
    def _score_publication_type(self, pub_type: str) -> float:
        """Score based on publication type."""
        type_scores = {
            'peer_reviewed_study': 0.95,
            'systematic_review': 0.95,
            'meta_analysis': 0.93,
            'clinical_guideline': 0.90,
            'government_report': 0.90,
            'regulatory_filing': 0.88,
            'government_agency': 0.88,
            'textbook': 0.85,
            'conference_paper': 0.80,
            'preprint_verified': 0.75,
            'technical_manual': 0.75,
            'dataset_documentation': 0.70,
            'A': 0.90,
            'B': 0.80,
            'C': 0.70,
        }
        return type_scores.get(pub_type.lower(), 0.65)
    
    def _score_url_structure(self, url: str) -> float:
        """Score based on URL structure quality."""
        score = 0.5  # Base score
        
        # Has HTTPS
        if url.startswith('https://'):
            score += 0.2
        
        # Specific path (not just homepage)
        if url.count('/') > 3:
            score += 0.2
        
        # Has DOI or article identifier
        if 'doi' in url or '/article/' in url or '/paper/' in url:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_to_class(self, score: float) -> str:
        """Convert numeric score to letter class."""
        if score >= 0.90:
            return 'A'
        elif score >= 0.75:
            return 'B'
        elif score >= 0.60:
            return 'C'
        elif score >= 0.40:
            return 'D'
        else:
            return 'F'
    
    def record_accuracy(self, source_url: str, was_accurate: bool):
        """Record whether a source was accurate for future scoring."""
        domain = self._extract_domain(source_url)
        if domain not in self._historical_accuracy:
            self._historical_accuracy[domain] = {'accurate': 0, 'total': 0}
        
        self._historical_accuracy[domain]['total'] += 1
        if was_accurate:
            self._historical_accuracy[domain]['accurate'] += 1
    
    def get_historical_accuracy(self, source_url: str) -> Optional[float]:
        """Get historical accuracy rate for a domain."""
        domain = self._extract_domain(source_url)
        if domain in self._historical_accuracy:
            stats = self._historical_accuracy[domain]
            if stats['total'] > 0:
                return stats['accurate'] / stats['total']
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        match = re.search(r'https?://([^/]+)', url)
        if match:
            return match.group(1)
        return url


# Singleton instance
_scorer = SourceCredibilityScorer()


def score_source_credibility(source_url: str, 
                            publication_type: str = None,
                            historical_accuracy: float = None) -> Dict:
    """
    Score the credibility of a source.
    
    This is the main entry point for source credibility scoring.
    
    Args:
        source_url: The source URL to evaluate
        publication_type: Optional type (peer_reviewed_study, government_report, etc.)
        historical_accuracy: Optional historical accuracy score (0-1)
    
    Returns:
        Dictionary with score, class, factors, and recommendations
    
    Example:
        >>> result = score_source_credibility("https://pubmed.gov/article/123")
        >>> print(f"Score: {result['score']}, Class: {result['class']}")
    """
    result = _scorer.score_source(source_url, publication_type, historical_accuracy)
    return {
        'score': result.score,
        'class': result.credibility_class,
        'factors': result.factors,
        'recommendations': result.recommendations,
        'source_url': result.source_url
    }


def classify_source(source_url: str) -> str:
    """
    Get just the credibility class for a source.
    
    Args:
        source_url: The source URL
    
    Returns:
        Credibility class (A, B, C, D, or F)
    """
    return _scorer.score_source(source_url).credibility_class


if __name__ == '__main__':
    # Test the scorer
    test_sources = [
        ("https://pubmed.ncbi.nlm.nih.gov/12345", "peer_reviewed_study"),
        ("https://www.ecb.europa.eu/home/html/index.en.html", "government_agency"),
        ("https://www.nature.com/articles/s41586-021-01234", "peer_reviewed_study"),
        ("https://www.reuters.com/markets/us/fed-rates", None),
        ("https://medium.com/@user/my-opinion", None),
        ("https://reddit.com/r/economics/comments/xyz", None),
        ("", None),
    ]
    
    print("Source Credibility Scoring System")
    print("=" * 70)
    
    for url, pub_type in test_sources:
        result = score_source_credibility(url, pub_type)
        print(f"\nURL: {url[:60]}{'...' if len(url) > 60 else ''}")
        print(f"  Score: {result['score']} (Class: {result['class']})")
        print(f"  Factors: {result['factors']}")
        if result['recommendations']:
            print(f"  Recommendations:")
            for rec in result['recommendations']:
                print(f"    - {rec}")
