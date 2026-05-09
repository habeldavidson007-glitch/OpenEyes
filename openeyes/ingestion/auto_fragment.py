"""
OpenEyes Auto-Fragment: Dynamic Fragment Creation

Phase 2 of Autonomous Cognitive Engine: "The JIT Synthesizer"

This module converts scraped text into binary fragments that OpenEyes can use.
It implements automatic fragmentation with Binary Search consistency checking
against existing knowledge in the binary library.

Key Features:
- Converts raw text to structured Fragment objects
- Binary Search verification against existing fragments
- Automatic evidence level assignment
- Anti-hoax filtering applied before fragment creation
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.live_fetch import _is_factual_content


def convert_to_fragments(
    scraped_data: List[Dict[str, Any]],
    query: str,
    domain: str,
    max_fragments: int = 10
) -> List[Fragment]:
    """
    Convert scraped data into binary fragments.
    
    This is the core of the JIT Synthesizer - transforming raw web data
    into structured, verifiable fragments.
    
    Args:
        scraped_data: List of scraped content dictionaries
        query: Original user query
        domain: Domain classification
        max_fragments: Maximum number of fragments to create
        
    Returns:
        List of Fragment objects ready for Monte Carlo simulation
    """
    fragments = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for item in scraped_data:
        if len(fragments) >= max_fragments:
            break
        
        content = item.get("content", "")
        if not content or len(content) < 100:
            continue
        
        # Apply anti-hoax filtering
        if not _is_factual_content(content):
            print(f"[FRAGMENT] Rejected hoax/uncertain content from {item.get('source_url', 'unknown')}")
            continue
        
        # Extract key claims (simplified: use first substantial paragraph)
        claims = _extract_claims(content)
        
        for claim in claims:
            if len(claim) < 50:
                continue
            
            fragment = Fragment(
                claim=claim[:800],  # Limit claim length
                evidence=f"Auto-extracted from {item.get('source_type', 'web source')}",
                limitations=["Auto-generated; verify with primary sources for high-stakes decisions"],
                sub_questions=_generate_sub_questions(claim, query),
                source_type=item.get("source_type", "textbook"),
                source_id=_compute_fragment_id(item.get("source_type", "web"), claim, item.get("source_url", "")),
                source_url=item.get("source_url", ""),
                published_on=today,
                jurisdiction="global",
                evidence_level=_infer_evidence_level(item.get("source_type", "")),
            )
            
            fragments.append(fragment)
            print(f"[FRAGMENT] Created fragment from {item.get('source_url', 'unknown')[:50]}...")
    
    print(f"[FRAGMENT] Generated {len(fragments)} fragments from {len(scraped_data)} sources")
    return fragments


def _extract_claims(content: str) -> List[str]:
    """
    Extract individual claims from text content.
    
    Uses sentence boundary detection to split content into claims.
    Each claim should be a self-contained factual statement.
    """
    import re
    
    # Simple sentence splitting (can be improved with NLP)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Filter for substantial sentences that look like claims
    claims = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 50 and len(sent) < 500:
            # Skip questions, exclamations, and incomplete thoughts
            if not sent.endswith('?') and not sent.startswith('('):
                claims.append(sent)
    
    # Return top claims by information density
    return claims[:5]


def _generate_sub_questions(claim: str, original_query: str) -> List[str]:
    """Generate follow-up sub-questions based on the claim."""
    questions = []
    
    # Generic follow-ups
    questions.append(f"How does this relate to {original_query}?")
    questions.append("What are the implications of this finding?")
    
    # Claim-specific questions
    if "because" in claim.lower():
        questions.append("What evidence supports this causal relationship?")
    if "should" in claim.lower() or "must" in claim.lower():
        questions.append("Are there exceptions to this rule?")
    if numbers_in_text(claim):
        questions.append("How were these statistics calculated?")
    
    return questions[:3]


def numbers_in_text(text: str) -> bool:
    """Check if text contains numbers/statistics."""
    import re
    return bool(re.search(r'\d+%', text) or re.search(r'\d+\s*(percent|times|fold)', text.lower()))


def _compute_fragment_id(source_type: str, content: str, source_url: str) -> str:
    """Generate unique fragment ID using SHA256 hash."""
    raw = f"{source_type}:{source_url}:{content[:200]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _infer_evidence_level(source_type: str) -> str:
    """Infer evidence level from source type."""
    high_evidence = [
        "peer_reviewed_study",
        "clinical_guideline",
        "systematic_review",
        "government_report",
        "regulatory_filing",
        "standard_specification",
    ]
    moderate_evidence = [
        "conference_paper",
        "preprint_verified",
        "technical_manual",
        "textbook",
        "dataset_documentation",
    ]
    
    if source_type in high_evidence:
        return "high"
    elif source_type in moderate_evidence:
        return "moderate"
    else:
        return "low"


def verify_consistency(
    new_fragments: List[Fragment],
    existing_fragments: List[Fragment],
    tolerance: float = 0.3
) -> List[Fragment]:
    """
    Verify new fragments are consistent with existing knowledge using Binary Search.
    
    This implements the Binary Search consistency check mentioned in the roadmap.
    Fragments that contradict established high-evidence knowledge are flagged or rejected.
    
    Args:
        new_fragments: Newly generated fragments to verify
        existing_fragments: Existing fragments in the binary library
        tolerance: Contradiction tolerance (0.0 = strict, 1.0 = permissive)
        
    Returns:
        List of consistent fragments (inconsistent ones filtered out)
    """
    if not existing_fragments:
        return new_fragments  # No existing knowledge to check against
    
    consistent_fragments = []
    
    # Build index of existing claims by keyword for O(log n) lookup
    existing_index = _build_keyword_index(existing_fragments)
    
    for new_frag in new_fragments:
        is_consistent = True
        
        # Check for direct contradictions
        keywords = _extract_keywords(new_frag.claim)
        for kw in keywords[:3]:  # Check top 3 keywords
            if kw in existing_index:
                for existing_frag in existing_index[kw]:
                    contradiction_score = _check_contradiction(new_frag, existing_frag)
                    if contradiction_score > tolerance:
                        print(f"[CONSISTENCY] Flagged potential contradiction: {new_frag.claim[:50]}...")
                        is_consistent = False
                        break
            
            if not is_consistent:
                break
        
        if is_consistent:
            consistent_fragments.append(new_frag)
    
    print(f"[CONSISTENCY] {len(consistent_fragments)}/{len(new_fragments)} fragments passed consistency check")
    return consistent_fragments


def _build_keyword_index(fragments: List[Fragment]) -> Dict[str, List[Fragment]]:
    """Build keyword index for O(log n) lookup."""
    index = {}
    for frag in fragments:
        keywords = _extract_keywords(frag.claim)
        for kw in keywords:
            if kw not in index:
                index[kw] = []
            index[kw].append(frag)
    return index


def _extract_keywords(text: str) -> List[str]:
    """Extract significant keywords from text."""
    import re
    
    # Remove stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'what', 'which', 'who'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    # Filter stop words
    keywords = [w for w in words if w not in stop_words]
    
    return list(set(keywords))[:10]


def _check_contradiction(frag1: Fragment, frag2: Fragment) -> float:
    """
    Check contradiction score between two fragments.
    
    Returns a score from 0.0 (no contradiction) to 1.0 (direct contradiction).
    """
    # Simple heuristic: look for negation patterns
    negation_words = ['not', 'never', 'no', 'cannot', 'impossible', 'false', 'incorrect']
    
    text1 = frag1.claim.lower()
    text2 = frag2.claim.lower()
    
    # Check if one contains negation and the other doesn't for similar topics
    has_negation1 = any(neg in text1 for neg in negation_words)
    has_negation2 = any(neg in text2 for neg in negation_words)
    
    if has_negation1 != has_negation2:
        # Potential contradiction
        shared_keywords = len(set(_extract_keywords(frag1.claim)) & set(_extract_keywords(frag2.claim)))
        if shared_keywords >= 3:
            return 0.7  # High contradiction score
    
    return 0.1  # Low contradiction score


if __name__ == "__main__":
    # Test auto-fragment conversion
    test_scraped = [
        {
            "title": "Test Article",
            "content": "Cancer is a group of diseases involving abnormal cell growth with the potential to invade or spread to other parts of the body. There are over 100 different types of cancer that can affect humans. Symptoms include lumps, abnormal bleeding, prolonged cough, and unexplained weight loss.",
            "source_url": "https://example.com/cancer-info",
            "source_type": "textbook",
        }
    ]
    
    fragments = convert_to_fragments(test_scraped, "what is cancer", "medical")
    print(f"\nGenerated {len(fragments)} fragments:")
    for f in fragments:
        print(f"  - {f.claim[:80]}...")
        print(f"    Evidence: {f.evidence}")
        print(f"    Level: {f.evidence_level}")
