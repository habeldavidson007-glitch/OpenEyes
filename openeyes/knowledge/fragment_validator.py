"""
Fragment Validation & Quality Scoring Module

Provides dynamic quality scoring for fragments based on:
- Verification status
- Source credibility
- Evidence level
- Cross-domain corroboration
- Recency
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, date

from openeyes.knowledge.fragments import Fragment


@dataclass
class QualityMetrics:
    """Quality metrics for a fragment."""
    verification_score: float = 0.0      # 0.0-1.0
    source_score: float = 0.0            # 0.0-1.0
    evidence_score: float = 0.0          # 0.0-1.0
    recency_score: float = 0.0           # 0.0-1.0
    corroboration_score: float = 0.0     # 0.0-1.0
    overall_quality: float = 0.0         # 0.0-1.0


# Source type credibility weights
SOURCE_CREDIBILITY = {
    "peer_reviewed_study": 1.0,
    "government_report": 0.95,
    "academic_textbook": 0.90,
    "reputable_news": 0.80,
    "industry_report": 0.75,
    "expert_opinion": 0.70,
    "general_web": 0.50,
    "user_generated": 0.30,
    "unknown": 0.40,
}

# Evidence level weights
EVIDENCE_LEVELS = {
    "high": 1.0,
    "moderate": 0.7,
    "low": 0.4,
    "very_low": 0.2,
}

# Verification status weights
VERIFICATION_WEIGHTS = {
    "peer_reviewed": 1.0,
    "verified": 0.85,
    "community_verified": 0.70,
    "unverified": 0.50,
}


def calculate_verification_score(fragment: Fragment) -> float:
    """Calculate verification score based on verification status."""
    status = getattr(fragment, 'verification_status', 'unverified')
    base_score = VERIFICATION_WEIGHTS.get(status, 0.5)
    
    # Bonus for having verification date and verifier
    if getattr(fragment, 'verification_date', ''):
        base_score = min(1.0, base_score + 0.1)
    if getattr(fragment, 'verified_by', ''):
        base_score = min(1.0, base_score + 0.05)
    
    return base_score


def calculate_source_score(fragment: Fragment) -> float:
    """Calculate source credibility score."""
    source_type = getattr(fragment, 'source_type', 'unknown')
    base_score = SOURCE_CREDIBILITY.get(source_type, 0.4)
    
    # Bonus for having source URL
    if getattr(fragment, 'source_url', ''):
        base_score = min(1.0, base_score + 0.05)
    
    # Bonus for having publication date
    if getattr(fragment, 'published_on', ''):
        base_score = min(1.0, base_score + 0.05)
    
    return base_score


def calculate_evidence_score(fragment: Fragment) -> float:
    """Calculate evidence quality score."""
    evidence_level = getattr(fragment, 'evidence_level', 'moderate')
    base_score = EVIDENCE_LEVELS.get(evidence_level, 0.5)
    
    # Consider contradiction flags
    contradictions = getattr(fragment, 'contradiction_flags', [])
    if contradictions:
        penalty = len(contradictions) * 0.1
        base_score = max(0.0, base_score - penalty)
    
    return base_score


def calculate_recency_score(fragment: Fragment) -> float:
    """Calculate recency score based on publication date."""
    published = getattr(fragment, 'published_on', '')
    if not published:
        return 0.5  # Default for unknown dates
    
    try:
        pub_date = date.fromisoformat(published)
        today = date.today()
        days_old = (today - pub_date).days
        
        # Score decay over time
        if days_old < 365:  # Less than 1 year
            return 1.0
        elif days_old < 730:  # 1-2 years
            return 0.9
        elif days_old < 1825:  # 2-5 years
            return 0.7
        elif days_old < 3650:  # 5-10 years
            return 0.5
        else:  # Older than 10 years
            return 0.3
    except (ValueError, TypeError):
        return 0.5


def calculate_corroboration_score(fragment: Fragment, all_fragments: List[Fragment]) -> float:
    """Calculate cross-domain corroboration score."""
    if not all_fragments or len(all_fragments) == 1:
        return 0.5  # No corroboration possible
    
    claim = getattr(fragment, 'claim', '').lower()
    corroborating = 0
    
    for other in all_fragments:
        if other is fragment:
            continue
        other_claim = getattr(other, 'claim', '').lower()
        
        # Simple similarity check (can be enhanced with NLP)
        if any(word in other_claim for word in claim.split() if len(word) > 4):
            corroborating += 1
    
    # Score based on corroboration ratio
    ratio = corroborating / (len(all_fragments) - 1)
    return 0.5 + (ratio * 0.5)  # Base 0.5, up to 1.0 with full corroboration


def calculate_fragment_quality(fragment: Fragment, all_fragments: Optional[List[Fragment]] = None) -> QualityMetrics:
    """
    Calculate comprehensive quality metrics for a fragment.
    
    Args:
        fragment: The fragment to evaluate
        all_fragments: Optional list of all fragments for corroboration scoring
    
    Returns:
        QualityMetrics with all scores
    """
    if all_fragments is None:
        all_fragments = [fragment]
    
    verification = calculate_verification_score(fragment)
    source = calculate_source_score(fragment)
    evidence = calculate_evidence_score(fragment)
    recency = calculate_recency_score(fragment)
    corroboration = calculate_corroboration_score(fragment, all_fragments)
    
    # Weighted overall quality
    # Weights: Verification 30%, Source 25%, Evidence 25%, Recency 10%, Corroboration 10%
    overall = (
        verification * 0.30 +
        source * 0.25 +
        evidence * 0.25 +
        recency * 0.10 +
        corroboration * 0.10
    )
    
    return QualityMetrics(
        verification_score=round(verification, 3),
        source_score=round(source, 3),
        evidence_score=round(evidence, 3),
        recency_score=round(recency, 3),
        corroboration_score=round(corroboration, 3),
        overall_quality=round(overall, 3)
    )


def calculate_confidence_from_quality(metrics: QualityMetrics) -> float:
    """
    Convert quality metrics to confidence percentage (0-100).
    
    This replaces hardcoded confidence values with dynamic calculation.
    """
    # Base confidence from overall quality
    base_confidence = metrics.overall_quality * 100.0
    
    # Adjustments based on specific factors
    if metrics.verification_score >= 0.85:
        base_confidence = min(100.0, base_confidence + 5.0)
    elif metrics.verification_score < 0.5:
        base_confidence = max(0.0, base_confidence - 10.0)
    
    if metrics.evidence_score >= 0.8:
        base_confidence = min(100.0, base_confidence + 5.0)
    elif metrics.evidence_score < 0.4:
        base_confidence = max(0.0, base_confidence - 10.0)
    
    return round(base_confidence, 2)


def get_domain_default_confidence(domain: str) -> float:
    """
    Get default confidence baseline for domains without sufficient fragments.
    
    This replaces the hardcoded 66.0 value with domain-appropriate baselines.
    """
    domain_baselines = {
        "healthcare": 65.0,   # High stakes, conservative
        "medical": 65.0,
        "economy": 70.0,      # Well-documented data
        "investment": 68.0,
        "governance": 67.0,
        "legal": 66.0,
        "engineering": 72.0,  # Technical precision
        "education": 70.0,
        "science": 73.0,
        "general": 60.0,      # Lower baseline for general queries
    }
    
    return domain_baselines.get(domain.lower(), 60.0)


if __name__ == "__main__":
    # Test fragment quality calculation
    print("=" * 80)
    print("FRAGMENT QUALITY VALIDATION TEST")
    print("=" * 80)
    
    # Create test fragment
    test_frag = Fragment(
        claim="Test claim about healthcare",
        evidence="Supporting evidence",
        limitations=[],
        sub_questions=[],
        source_type="peer_reviewed_study",
        source_id="test_001",
        published_on="2024-01-15",
        evidence_level="high",
        verification_status="verified",
        verification_date="2024-01-20",
        verified_by="Dr. Test",
        quality_score=0.0,
        contradiction_flags=[]
    )
    
    metrics = calculate_fragment_quality(test_frag)
    confidence = calculate_confidence_from_quality(metrics)
    
    print(f"\nTest Fragment Quality Metrics:")
    print(f"  Verification: {metrics.verification_score:.3f}")
    print(f"  Source: {metrics.source_score:.3f}")
    print(f"  Evidence: {metrics.evidence_score:.3f}")
    print(f"  Recency: {metrics.recency_score:.3f}")
    print(f"  Corroboration: {metrics.corroboration_score:.3f}")
    print(f"  Overall Quality: {metrics.overall_quality:.3f}")
    print(f"  Calculated Confidence: {confidence:.2f}%")
    
    print(f"\nDomain Baselines:")
    for domain in ["healthcare", "economy", "general", "investment"]:
        baseline = get_domain_default_confidence(domain)
        print(f"  {domain}: {baseline:.1f}%")
