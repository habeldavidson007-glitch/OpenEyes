"""
Phase 4: Fuzzy Logic & Rich Shorthand Optimization
Implements continuous confidence metrics and human analogy framing
for resolving data contradictions and serving expert-level responses.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re


@dataclass
class FuzzyConfidenceInput:
    """Input parameters for fuzzy confidence calculation."""
    freshness_coefficient: float = 1.0  # F: 0.0-1.0 based on data recency
    peer_review_status: float = 1.0     # P: 0.0-1.0 based on verification level
    source_ranking: float = 1.0         # R: 0.0-1.0 based on source authority
    
    # Optional additional factors
    fragment_count: int = 0
    contradiction_count: int = 0
    cross_domain_support: float = 0.0


@dataclass
class FuzzyConfidenceResult:
    """Result of fuzzy confidence evaluation."""
    trust_score: float          # T: Aggregate trust score (0.0-1.0)
    confidence_class: str       # 'HIGH', 'MEDIUM', 'LOW'
    response_mode: str          # 'ABSOLUTE_TRUTH', 'AMBIGUOUS', 'UNCERTAIN'
    recommended_template: str   # Which payload variant to use
    explanation: str


class FuzzyConfidenceEvaluator:
    """
    Phase 4.1: Fuzzy Confidence Metric Evaluation
    
    Swaps strict binary Boolean values for continuous numeric
    metrics calculated between 0.0 and 1.0.
    
    Formula: T = (F × 0.5) + (P × 0.3) + (R × 0.2)
    Where:
      - F is the freshness coefficient
      - P is the peer-review status
      - R is the source ranking
    """
    
    # Weight coefficients (Section 4.1)
    WEIGHT_FRESHNESS = 0.5
    WEIGHT_PEER_REVIEW = 0.3
    WEIGHT_SOURCE_RANKING = 0.2
    
    # Confidence thresholds (Updated per production calibration)
    # HIGH: ≥75%, MEDIUM: 55-74%, LOW: <55%
    HIGH_CONFIDENCE_THRESHOLD = 0.75
    MEDIUM_CONFIDENCE_THRESHOLD = 0.55
    
    def __init__(self):
        pass
    
    def calculate_trust_score(self, inputs: FuzzyConfidenceInput) -> float:
        """
        Calculate aggregate trust score using weighted formula.
        
        T = (F × 0.5) + (P × 0.3) + (R × 0.2)
        """
        # Clamp inputs to valid range
        F = max(0.0, min(1.0, inputs.freshness_coefficient))
        P = max(0.0, min(1.0, inputs.peer_review_status))
        R = max(0.0, min(1.0, inputs.source_ranking))
        
        # Apply formula
        T = (F * self.WEIGHT_FRESHNESS) + \
            (P * self.WEIGHT_PEER_REVIEW) + \
            (R * self.WEIGHT_SOURCE_RANKING)
        
        return round(T, 3)
    
    def classify_confidence(self, trust_score: float) -> Tuple[str, str, str]:
        """
        Classify trust score into confidence class and response mode.
        
        Returns:
            Tuple of (confidence_class, response_mode, recommended_template)
        """
        if trust_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            return (
                'HIGH',
                'ABSOLUTE_TRUTH',
                'standard_payload'
            )
        elif trust_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return (
                'MEDIUM',
                'AMBIGUOUS',
                'ambiguous_payload'
            )
        else:
            return (
                'LOW',
                'UNCERTAIN',
                'uncertainty_template'
            )
    
    def evaluate(self, inputs: FuzzyConfidenceInput) -> FuzzyConfidenceResult:
        """
        Complete fuzzy confidence evaluation.
        
        Args:
            inputs: FuzzyConfidenceInput parameters
            
        Returns:
            FuzzyConfidenceResult with classification and recommendations
        """
        # Calculate trust score
        trust_score = self.calculate_trust_score(inputs)
        
        # Classify
        confidence_class, response_mode, template = self.classify_confidence(trust_score)
        
        # Generate explanation
        explanation = self._generate_explanation(trust_score, inputs)
        
        return FuzzyConfidenceResult(
            trust_score=trust_score,
            confidence_class=confidence_class,
            response_mode=response_mode,
            recommended_template=template,
            explanation=explanation
        )
    
    def _generate_explanation(self, trust_score: float, inputs: FuzzyConfidenceInput) -> str:
        """Generate human-readable explanation of confidence assessment."""
        if trust_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            base = "High confidence based on"
        elif trust_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            base = "Moderate confidence with some uncertainty due to"
        else:
            base = "Low confidence due to"
        
        factors = []
        if inputs.freshness_coefficient < 0.7:
            factors.append("outdated information")
        if inputs.peer_review_status < 0.7:
            factors.append("limited verification")
        if inputs.source_ranking < 0.7:
            factors.append("lower-tier sources")
        if inputs.contradiction_count > 0:
            factors.append(f"{inputs.contradiction_count} conflicting records")
        
        if not factors:
            factors.append("strong supporting evidence across all dimensions")
        
        return f"{base} {'; '.join(factors)}."


class HumanAnalogyFramer:
    """
    Phase 4.2: Human Analogy Framing
    
    Inserts mandatory text slots for short, high-impact descriptions
    directly inside knowledge nodes. Strips out dry academic explanations.
    
    Every structural data response must prioritize leading with a brief,
    conversational summary alongside a concrete real-world comparison
    before serving the citation block.
    """
    
    # Analogy templates by domain
    ANALOGY_TEMPLATES = {
        'economy': [
            "Like {comparison} - your {thing_stays_same} but {thing_gets_worse}.",
            "Similar to {comparison} - imagine {scenario}.",
            "Think of it as {comparison} - where {effect}.",
        ],
        'healthcare': [
            "Your body is like {comparison} - when {condition}, then {effect}.",
            "Similar to how {comparison} works - {explanation}.",
            "Think of it like {comparison} - {practical_impact}.",
        ],
        'investment': [
            "Like {comparison} - {risk_reward_tradeoff}.",
            "Similar to {comparison} - where {market_dynamic}.",
            "Think of it as {comparison} - {key_insight}.",
        ],
        'general': [
            "Like {comparison} - {simple_explanation}.",
            "Imagine {comparison} - that's similar to this.",
            "Think of it as {comparison} - {core_concept}.",
        ],
    }
    
    # Pre-built analogies for common concepts
    BUILT_IN_ANALOGIES = {
        'inflation': "Your paycheck stays the same size, but your grocery cart shrinks.",
        'interest_rates': "Like rent for money - the higher the rate, the more you pay to borrow.",
        'recession': "The economy catching a cold - everything slows down temporarily.",
        'stock_market': "A voting machine in the short term, weighing machine in the long term.",
        'insurance': "Paying a small amount now to avoid a huge bill later.",
        'vaccine': "Training your immune system like a fire drill prepares you for real emergencies.",
        'antibiotics': "Like sending special forces to kill bacteria invaders.",
        'diversification': "Not putting all your eggs in one basket.",
        'compound_interest': "Money having babies, and those babies having their own babies.",
    }
    
    def __init__(self):
        self._custom_analogies: Dict[str, str] = {}
    
    def get_builtin_analogy(self, concept: str) -> Optional[str]:
        """Get pre-built analogy for common concept."""
        concept_lower = concept.lower()
        
        # Direct match
        if concept_lower in self.BUILT_IN_ANALOGIES:
            return self.BUILT_IN_ANALOGIES[concept_lower]
        
        # Partial match
        for key, analogy in self.BUILT_IN_ANALOGIES.items():
            if key in concept_lower or concept_lower in key:
                return analogy
        
        return None
    
    def generate_shorthand(self, content: str, max_length: int = 80) -> str:
        """
        Generate punchy shorthand from detailed content.
        
        Extracts the core insight and expresses it conversationally.
        """
        # Remove academic filler
        filler_patterns = [
            r'it is important to note that\s+',
            r'furthermore,\s+',
            r'in addition,\s+',
            r'moreover,\s+',
            r'this suggests that\s+',
            r'research indicates that\s+',
        ]
        
        cleaned = content
        for pattern in filler_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Extract first meaningful sentence
        sentences = re.split(r'[.!?]+', cleaned)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < max_length:
                # Capitalize first letter
                return sentence[0].upper() + sentence[1:] + '.'
        
        # Fallback: truncate and clean
        if len(content) > max_length:
            return content[:max_length-3].rsplit(' ', 1)[0] + '...'
        
        return content
    
    def frame_response(self, concept: str, content: str, domain: str = 'general') -> Dict[str, str]:
        """
        Frame a complete response with shorthand and analogy.
        
        Args:
            concept: Main concept being explained
            content: Detailed content to summarize
            domain: Target domain for analogy selection
            
        Returns:
            Dictionary with 'shorthand', 'analogy', and 'full_response'
        """
        # Generate shorthand
        shorthand = self.generate_shorthand(content)
        
        # Try to get built-in analogy
        analogy = self.get_builtin_analogy(concept)
        
        # If no built-in, use template
        if not analogy:
            templates = self.ANALOGY_TEMPLATES.get(domain, self.ANALOGY_TEMPLATES['general'])
            # Use first template as default
            analogy = templates[0].format(
                comparison="a complex system",
                thing_stays_same="input remains constant",
                thing_gets_worse="output degrades",
                scenario="conditions change over time",
                effect="results vary",
                simple_explanation="multiple factors interact",
                practical_impact="outcomes depend on context",
                risk_reward_tradeoff="higher potential returns come with higher risks",
                market_dynamic="supply and demand fluctuate",
                key_insight="timing and selection matter",
                condition="one part malfunctions",
                explanation="the whole system is affected",
            )
        
        # Build full response
        full_response = f"{shorthand}\n\nAnalogy: {analogy}"
        
        return {
            'shorthand': shorthand,
            'analogy': analogy,
            'full_response': full_response,
            'concept': concept,
            'domain': domain,
        }
    
    def register_custom_analogy(self, concept: str, analogy: str):
        """Register a custom analogy for a concept."""
        self._custom_analogies[concept.lower()] = analogy
        self.BUILT_IN_ANALOGIES[concept.lower()] = analogy


# Singleton instances
_fuzzy_evaluator: Optional[FuzzyConfidenceEvaluator] = None
_analogy_framer: Optional[HumanAnalogyFramer] = None


def get_fuzzy_confidence_evaluator() -> FuzzyConfidenceEvaluator:
    """Get or create singleton FuzzyConfidenceEvaluator instance."""
    global _fuzzy_evaluator
    if _fuzzy_evaluator is None:
        _fuzzy_evaluator = FuzzyConfidenceEvaluator()
    return _fuzzy_evaluator


def get_human_analogy_framer() -> HumanAnalogyFramer:
    """Get or create singleton HumanAnalogyFramer instance."""
    global _analogy_framer
    if _analogy_framer is None:
        _analogy_framer = HumanAnalogyFramer()
    return _analogy_framer


def calculate_confidence_score(**kwargs) -> FuzzyConfidenceResult:
    """
    Convenience function to calculate fuzzy confidence score.
    
    Args:
        **kwargs: Parameters for FuzzyConfidenceInput
        
    Returns:
        FuzzyConfidenceResult
    """
    inputs = FuzzyConfidenceInput(**kwargs)
    return get_fuzzy_confidence_evaluator().evaluate(inputs)


def frame_answer_with_analogy(concept: str, content: str, domain: str = 'general') -> Dict[str, str]:
    """
    Convenience function to frame answer with shorthand and analogy.
    
    Args:
        concept: Main concept
        content: Detailed content
        domain: Target domain
        
    Returns:
        Dictionary with framed response components
    """
    return get_human_analogy_framer().frame_response(concept, content, domain)


if __name__ == "__main__":
    # Test Phase 4 components
    print("=" * 80)
    print("PHASE 4: FUZZY LOGIC & ANALOGY FRAMING TEST SUITE")
    print("=" * 80)
    
    # Test Fuzzy Confidence Evaluator
    print("\n--- FUZZY CONFIDENCE TESTS ---\n")
    
    evaluator = FuzzyConfidenceEvaluator()
    
    test_cases = [
        (
            "High confidence scenario",
            FuzzyConfidenceInput(
                freshness_coefficient=0.95,
                peer_review_status=0.90,
                source_ranking=0.85
            ),
            'HIGH'
        ),
        (
            "Medium confidence scenario",
            FuzzyConfidenceInput(
                freshness_coefficient=0.60,
                peer_review_status=0.70,
                source_ranking=0.65
            ),
            'MEDIUM'
        ),
        (
            "Low confidence scenario",
            FuzzyConfidenceInput(
                freshness_coefficient=0.30,
                peer_review_status=0.40,
                source_ranking=0.35
            ),
            'LOW'
        ),
        (
            "Contradictions present",
            FuzzyConfidenceInput(
                freshness_coefficient=0.80,
                peer_review_status=0.75,
                source_ranking=0.70,
                contradiction_count=3
            ),
            'MEDIUM'
        ),
    ]
    
    for desc, inputs, expected_class in test_cases:
        result = evaluator.evaluate(inputs)
        status = "✓" if result.confidence_class == expected_class else "✗"
        
        print(f"{status} {desc}")
        print(f"   Trust Score: {result.trust_score:.3f}")
        print(f"   Class: {result.confidence_class} (expected: {expected_class})")
        print(f"   Mode: {result.response_mode}")
        print(f"   Template: {result.recommended_template}")
        print(f"   Explanation: {result.explanation}")
        print()
    
    # Test Human Analogy Framer
    print("\n--- ANALOGY FRAMING TESTS ---\n")
    
    framer = HumanAnalogyFramer()
    
    test_content = [
        ("inflation", "Inflation is the rate at which the general level of prices for goods and services is rising, subsequently eroding purchasing power.", "economy"),
        ("interest rates", "Interest rates represent the cost of borrowing capital, determined by central bank policy and market forces.", "economy"),
        ("vaccines", "Vaccines work by stimulating the immune system to recognize and fight specific pathogens, providing immunity without causing disease.", "healthcare"),
        ("unknown concept", "This is a complex phenomenon with multiple interacting variables and contextual dependencies.", "general"),
    ]
    
    for concept, content, domain in test_content:
        result = framer.frame_response(concept, content, domain)
        
        print(f"Concept: {concept} ({domain})")
        print(f"   Shorthand: {result['shorthand']}")
        print(f"   Analogy: {result['analogy']}")
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
