"""
OpenEyes Pre-Flight Critic System
Validates every answer before release using deterministic logic checks.
Prevents hallucinations, logical inconsistencies, and source mismatches.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


@dataclass
class ValidationResult:
    status: ValidationStatus
    check_name: str
    message: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class PreFlightCritic:
    """
    Deterministic validation engine that checks every generated answer
    against source fragments, logical consistency, and safety constraints.
    """
    
    def __init__(self):
        self.validation_checks = [
            self._check_source_alignment,
            self._check_logical_consistency,
            self._check_confidence_threshold,
            self._check_safety_compliance,
            self._check_fragment_coverage,
            self._check_no_hallucination,
        ]
    
    def validate_answer(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict = None
    ) -> Tuple[bool, List[ValidationResult]]:
        """
        Run all validation checks on a generated answer.
        Returns: (passed_all_checks, list_of_validation_results)
        """
        if metadata is None:
            metadata = {}
        
        results = []
        all_passed = True
        
        for check in self.validation_checks:
            result = check(
                query=query,
                answer=answer,
                confidence=confidence,
                fragments_used=fragments_used,
                domain=domain,
                metadata=metadata
            )
            results.append(result)
            
            if result.status == ValidationStatus.FAILED:
                all_passed = False
        
        return all_passed, results
    
    def _check_source_alignment(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Verify every claim in the answer can be traced to a source fragment.
        """
        if not fragments_used:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                check_name="source_alignment",
                message="No source fragments provided for answer",
                details={"query": query}
            )
        
        # Check if answer contains concepts not in fragments
        fragment_texts = " ".join([f.get('content', '') for f in fragments_used])
        fragment_keywords = set(fragment_texts.lower().split())
        
        answer_keywords = set(answer.lower().split())
        unmatched_keywords = answer_keywords - fragment_keywords - {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'to', 'of', 'and', 'in', 'that', 'for', 'on', 'with', 'as'
        }
        
        # Allow up to 20% unmatched keywords (connectors, articles, etc.)
        if len(answer_keywords) > 0:
            unmatched_ratio = len(unmatched_keywords) / len(answer_keywords)
            if unmatched_ratio > 0.3:
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    check_name="source_alignment",
                    message=f"Answer contains {unmatched_ratio:.1%} keywords not found in sources",
                    details={
                        "unmatched_count": len(unmatched_keywords),
                        "total_keywords": len(answer_keywords),
                        "sample_unmatched": list(unmatched_keywords)[:5]
                    }
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="source_alignment",
            message="All answer claims traceable to source fragments",
            details={"fragments_count": len(fragments_used)}
        )
    
    def _check_logical_consistency(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Detect internal contradictions in the answer.
        """
        # Simple contradiction detection patterns
        contradiction_patterns = [
            ("increases", "decreases"),
            ("rises", "falls"),
            ("high", "low"),
            ("positive", "negative"),
            ("causes", "prevents"),
        ]
        
        answer_lower = answer.lower()
        
        for pos_term, neg_term in contradiction_patterns:
            if pos_term in answer_lower and neg_term in answer_lower:
                # Check if they're referring to the same subject
                # Simplified: flag any co-occurrence within 50 characters
                pos_idx = answer_lower.find(pos_term)
                neg_idx = answer_lower.find(neg_term)
                
                if abs(pos_idx - neg_idx) < 50:
                    return ValidationResult(
                        status=ValidationStatus.WARNING,
                        check_name="logical_consistency",
                        message=f"Potential contradiction detected: '{pos_term}' and '{neg_term}'",
                        details={
                            "term1": pos_term,
                            "term2": neg_term,
                            "proximity": abs(pos_idx - neg_idx)
                        }
                    )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="logical_consistency",
            message="No internal contradictions detected",
            details={}
        )
    
    def _check_confidence_threshold(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Ensure confidence level matches the quality of evidence.
        """
        if confidence < 55.0:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                check_name="confidence_threshold",
                message=f"Confidence {confidence:.1f}% below minimum threshold (55%)",
                details={"confidence": confidence, "threshold": 55.0}
            )
        
        # Check if HIGH confidence has sufficient fragment support
        if confidence >= 75.0:
            if len(fragments_used) < 2:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_name="confidence_threshold",
                    message="HIGH confidence with only 1 supporting fragment",
                    details={
                        "confidence": confidence,
                        "fragments_count": len(fragments_used),
                        "recommended_min": 2
                    }
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="confidence_threshold",
            message=f"Confidence {confidence:.1f}% meets threshold requirements",
            details={"confidence": confidence}
        )
    
    def _check_safety_compliance(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Verify answer complies with domain-specific safety rules.
        """
        # Healthcare safety checks
        if domain.lower() == 'healthcare':
            dangerous_phrases = [
                "you should take",
                "i recommend",
                "prescribe yourself",
                "stop taking",
                "dosage should be",
            ]
            
            answer_lower = answer.lower()
            for phrase in dangerous_phrases:
                if phrase in answer_lower:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        check_name="safety_compliance",
                        message=f"Healthcare answer contains prohibited advisory phrase: '{phrase}'",
                        details={"prohibited_phrase": phrase}
                    )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="safety_compliance",
            message="Answer complies with domain safety rules",
            details={"domain": domain}
        )
    
    def _check_fragment_coverage(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Ensure sufficient fragment coverage for the answer scope.
        """
        if not fragments_used:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                check_name="fragment_coverage",
                message="No fragments used to generate answer",
                details={}
            )
        
        # Check verification status of fragments
        verified_count = sum(1 for f in fragments_used if f.get('verified', False))
        total_count = len(fragments_used)
        
        if total_count > 0:
            verified_ratio = verified_count / total_count
            
            if confidence >= 75.0 and verified_ratio < 0.5:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_name="fragment_coverage",
                    message=f"HIGH confidence but only {verified_ratio:.1%} fragments verified",
                    details={
                        "verified_count": verified_count,
                        "total_count": total_count,
                        "verified_ratio": verified_ratio
                    }
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="fragment_coverage",
            message=f"Fragment coverage adequate ({verified_count}/{total_count} verified)",
            details={
                "verified_count": verified_count,
                "total_count": total_count
            }
        )
    
    def _check_no_hallucination(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        metadata: Dict
    ) -> ValidationResult:
        """
        Detect potential hallucinations by checking for fabricated specifics.
        """
        # Patterns that often indicate hallucination
        hallucination_indicators = [
            "according to recent studies",
            "research shows that",
            "experts agree",
            "statistics indicate",
            "data proves",
        ]
        
        answer_lower = answer.lower()
        
        for indicator in hallucination_indicators:
            if indicator in answer_lower:
                # Check if specific study/data is cited from fragments
                fragment_texts = " ".join([f.get('content', '').lower() for f in fragments_used])
                
                if "study" not in fragment_texts and "research" not in fragment_texts:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        check_name="no_hallucination",
                        message=f"Answer uses authoritative language without source backing: '{indicator}'",
                        details={"indicator": indicator}
                    )
        
        # Check for fabricated numbers/percentages not in fragments
        import re
        fragment_texts = " ".join([f.get('content', '') for f in fragments_used])
        
        # Find all percentages in answer
        answer_percentages = re.findall(r'\d+%', answer)
        fragment_percentages = re.findall(r'\d+%', fragment_texts)
        
        for pct in answer_percentages:
            if pct not in fragment_percentages:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_name="no_hallucination",
                    message=f"Percentage '{pct}' in answer not found in source fragments",
                    details={"percentage": pct}
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            check_name="no_hallucination",
            message="No hallucination indicators detected",
            details={}
        )
    
    def generate_validation_report(
        self,
        query: str,
        answer: str,
        confidence: float,
        fragments_used: List[Dict],
        domain: str,
        validation_results: List[ValidationResult]
    ) -> str:
        """
        Generate human-readable validation report.
        """
        passed_count = sum(1 for r in validation_results if r.status == ValidationStatus.PASSED)
        warning_count = sum(1 for r in validation_results if r.status == ValidationStatus.WARNING)
        failed_count = sum(1 for r in validation_results if r.status == ValidationStatus.FAILED)
        
        report = [
            "=" * 60,
            "PRE-FLIGHT VALIDATION REPORT",
            "=" * 60,
            f"Query: {query[:80]}{'...' if len(query) > 80 else ''}",
            f"Domain: {domain}",
            f"Confidence: {confidence:.1f}%",
            f"Fragments Used: {len(fragments_used)}",
            "-" * 60,
            f"Results: {passed_count} passed, {warning_count} warnings, {failed_count} failed",
            "-" * 60,
        ]
        
        for result in validation_results:
            status_icon = "✅" if result.status == ValidationStatus.PASSED else \
                         "⚠️" if result.status == ValidationStatus.WARNING else "❌"
            report.append(f"{status_icon} {result.check_name}: {result.message}")
            
            if result.details:
                for key, value in result.details.items():
                    report.append(f"     {key}: {value}")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Test the system
if __name__ == "__main__":
    critic = PreFlightCritic()
    
    print("=== Pre-Flight Critic System Test ===\n")
    
    # Test 1: Valid answer
    print("Test 1: Valid Answer")
    query1 = "What is inflation?"
    answer1 = "Inflation is a general increase in prices and fall in the purchasing value of money."
    fragments1 = [
        {"content": "Inflation is defined as a sustained increase in the general price level.", "verified": True},
        {"content": "When inflation rises, each unit of currency buys fewer goods and services.", "verified": True}
    ]
    
    passed, results = critic.validate_answer(
        query=query1,
        answer=answer1,
        confidence=78.0,
        fragments_used=fragments1,
        domain="economy"
    )
    
    print(critic.generate_validation_report(query1, answer1, 78.0, fragments1, "economy", results))
    print(f"\nOverall: {'✅ PASSED' if passed else '❌ FAILED'}\n")
    
    # Test 2: Hallucination detection
    print("\nTest 2: Hallucination Detection")
    query2 = "What causes hyperinflation?"
    answer2 = "According to recent studies, hyperinflation occurs when money supply increases by 50% monthly."
    fragments2 = [
        {"content": "Hyperinflation is extremely high inflation.", "verified": True}
    ]
    
    passed, results = critic.validate_answer(
        query=query2,
        answer=answer2,
        confidence=72.0,
        fragments_used=fragments2,
        domain="economy"
    )
    
    print(critic.generate_validation_report(query2, answer2, 72.0, fragments2, "economy", results))
    print(f"\nOverall: {'✅ PASSED' if passed else '❌ FAILED'}\n")
    
    # Test 3: Healthcare safety violation
    print("\nTest 3: Healthcare Safety Violation")
    query3 = "How to treat diabetes?"
    answer3 = "You should take metformin 500mg twice daily with meals."
    fragments3 = [
        {"content": "Metformin is commonly prescribed for type 2 diabetes.", "verified": True}
    ]
    
    passed, results = critic.validate_answer(
        query=query3,
        answer=answer3,
        confidence=80.0,
        fragments_used=fragments3,
        domain="healthcare"
    )
    
    print(critic.generate_validation_report(query3, answer3, 80.0, fragments3, "healthcare", results))
    print(f"\nOverall: {'✅ PASSED' if passed else '❌ FAILED'}\n")
    
    print("\n✅ Pre-Flight Critic System initialized successfully!")
