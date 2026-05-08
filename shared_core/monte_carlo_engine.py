"""
Monte Carlo Engine for OpenEyes

Generalized from E-AR's evolution/monte_carlo.py.
This module knows nothing about OpenEyes or E-AR specifically.
It operates on abstract candidates, weights, and scores.
Domain meaning is injected by the calling layer.

For OpenEyes: The `primitives` parameter will be knowledge fragments,
not E+ syntax primitives. The `evaluate_composition` function will need
OpenEyes-specific evaluators injected — credibility validators, factual
consistency checkers, philosophical alignment scorers.
"""

import random
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# =============================================================================
# Key Constants (inherited from E-AR, review before changing)
# =============================================================================

score_threshold = 60        # Minimum mean score to be considered viable
variance_threshold = 500    # Maximum variance — set for 5-evaluator diversity
survival_prob_threshold = 0.4  # Fraction of simulations that must exceed score_threshold


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class CompositionResult:
    """Result of evaluating a single composition."""
    mean_score: float
    variance: float
    worst_case: float
    survival_probability: float
    raw_scores: List[float] = field(default_factory=list)
    
    def is_viable(self) -> bool:
        """Check if this composition meets all viability criteria."""
        return (
            self.mean_score >= score_threshold and
            self.variance < variance_threshold and
            self.survival_probability >= survival_prob_threshold
        )


@dataclass
class MonteCarloWinner:
    """The winning composition from a Monte Carlo evolution run."""
    composition: List[Any]
    score: float
    variance: float
    survival_probability: float
    num_simulations: int


# =============================================================================
# Core Functions
# =============================================================================

def generate_composition(
    primitives: List[Dict[str, Any]],
    min_size: int = 1,
    max_size: int = 5,
    scenario: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None
) -> List[Any]:
    """
    Generates one candidate set from weighted primitives/fragments.
    
    Args:
        primitives: List of candidate primitives/fragments. Each should have an 'id' field.
        min_size: Minimum number of items in the composition.
        max_size: Maximum number of items in the composition.
        scenario: Optional scenario dict. If it has 'expected_constructs' or 
                  'expected_fragments', boosts matching item weights by 1.5×.
        weights: Optional dict mapping primitive/fragment IDs to weights.
                 If not provided, uses uniform weights.
    
    Returns:
        A list of selected primitives/fragments forming one candidate composition.
    """
    if not primitives:
        return []
    
    # Determine composition size
    size = random.randint(min_size, max_size)
    size = min(size, len(primitives))  # Can't select more than available
    
    # Build weight distribution
    if weights is None:
        weights = {p.get('id', i): 1.0 for i, p in enumerate(primitives)}
    
    # Apply scenario-based boosts if applicable
    boosted_weights = weights.copy()
    if scenario:
        expected_items = scenario.get('expected_constructs') or scenario.get('expected_fragments', [])
        for prim in primitives:
            prim_id = prim.get('id', '')
            tags = prim.get('tags', [])
            
            # Check if this primitive matches any expected item
            if prim_id in expected_items or any(tag in expected_items for tag in tags):
                boosted_weights[prim_id] = boosted_weights.get(prim_id, 1.0) * 1.5
    
    # Normalize weights for selection
    total_weight = sum(boosted_weights.get(p.get('id', i), 1.0) for i, p in enumerate(primitives))
    if total_weight == 0:
        total_weight = 1.0
    
    # Weighted random selection without replacement
    selected = []
    available = primitives.copy()
    
    for _ in range(size):
        if not available:
            break
        
        # Calculate weights for available items
        avail_weights = [
            boosted_weights.get(p.get('id', i), 1.0) 
            for i, p in enumerate(available)
        ]
        total_avail = sum(avail_weights)
        
        if total_avail == 0:
            # Fall back to uniform selection
            idx = random.randint(0, len(available) - 1)
        else:
            # Weighted selection
            r = random.random() * total_avail
            cumulative = 0.0
            idx = 0
            for i, w in enumerate(avail_weights):
                cumulative += w
                if r <= cumulative:
                    idx = i
                    break
        
        selected.append(available.pop(idx))
    
    return selected


def evaluate_composition(
    composition: List[Any],
    evaluators: Optional[List[Callable[[List[Any]], float]]] = None,
    num_simulations: int = 10
) -> CompositionResult:
    """
    Runs pressure evaluators on a composition across multiple simulations.
    
    Args:
        composition: The candidate composition to evaluate.
        evaluators: List of evaluator functions. Each takes a composition and 
                    returns a score (0-100). If None, uses a default evaluator.
        num_simulations: Number of simulation runs to perform.
    
    Returns:
        CompositionResult with mean_score, variance, worst_case, survival_probability.
    """
    if not composition:
        return CompositionResult(
            mean_score=0.0,
            variance=0.0,
            worst_case=0.0,
            survival_probability=0.0
        )
    
    # Default evaluator if none provided
    if evaluators is None:
        evaluators = [_default_evaluator]
    
    # Run simulations
    all_scores = []
    
    for _ in range(num_simulations):
        sim_scores = []
        for evaluator in evaluators:
            try:
                score = evaluator(composition)
                sim_scores.append(score)
            except Exception:
                # Evaluator failed, treat as low score
                sim_scores.append(0.0)
        
        # Aggregate scores from all evaluators for this simulation
        if sim_scores:
            sim_avg = sum(sim_scores) / len(sim_scores)
            all_scores.append(sim_avg)
    
    if not all_scores:
        return CompositionResult(
            mean_score=0.0,
            variance=0.0,
            worst_case=0.0,
            survival_probability=0.0
        )
    
    # Calculate statistics
    mean_score = sum(all_scores) / len(all_scores)
    
    # Variance calculation
    variance = sum((s - mean_score) ** 2 for s in all_scores) / len(all_scores)
    
    # Worst case
    worst_case = min(all_scores)
    
    # Survival probability: fraction of simulations above threshold
    surviving_count = sum(1 for s in all_scores if s >= score_threshold)
    survival_probability = surviving_count / len(all_scores)
    
    return CompositionResult(
        mean_score=mean_score,
        variance=variance,
        worst_case=worst_case,
        survival_probability=survival_probability,
        raw_scores=all_scores
    )


def _default_evaluator(composition: List[Any]) -> float:
    """
    Default evaluator for testing purposes.
    In production, inject domain-specific evaluators.
    
    For OpenEyes, this would be replaced with credibility validators,
    factual consistency checkers, etc.
    """
    # Placeholder: returns a random score for demonstration
    # In real usage, this should be replaced with actual evaluation logic
    base_score = 50.0
    
    # Add some variation based on composition characteristics
    if composition:
        # Bonus for having multiple items (diversity)
        base_score += min(len(composition) * 5, 20)
        
        # Random noise to simulate evaluator uncertainty
        noise = random.gauss(0, 15)
        base_score += noise
    
    return max(0.0, min(100.0, base_score))


def monte_carlo_evolve(
    primitives: List[Dict[str, Any]],
    min_size: int = 1,
    max_size: int = 5,
    num_samples: int = 50,
    stability_threshold: float = 0.3,
    survival_threshold: float = 0.7,
    scenario: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
    evaluators: Optional[List[Callable[[List[Any]], float]]] = None
) -> Optional[MonteCarloWinner]:
    """
    Full Monte Carlo evolution loop.
    
    Generates N candidate compositions, evaluates each, filters by survival
    criteria, and returns the best viable candidate.
    
    Args:
        primitives: Pool of candidate primitives/fragments to sample from.
        min_size: Minimum composition size.
        max_size: Maximum composition size.
        num_samples: Number of candidate compositions to generate and evaluate.
        stability_threshold: Alias for variance_threshold (normalized 0-1 scale).
                            Converted to absolute variance using score range.
        survival_threshold: Minimum survival probability required.
        scenario: Optional scenario for weight boosting.
        weights: Optional initial weights for primitives.
        evaluators: List of evaluator functions.
    
    Returns:
        MonteCarloWinner if a viable candidate is found, None otherwise.
    """
    if not primitives:
        return None
    
    # Convert normalized stability threshold to absolute variance
    # Assuming score range is 0-100, variance threshold = stability_threshold * 1000
    # But we use the global variance_threshold constant for consistency
    effective_variance_threshold = variance_threshold
    
    viable_candidates = []
    
    for _ in range(num_samples):
        # Generate candidate composition
        composition = generate_composition(
            primitives=primitives,
            min_size=min_size,
            max_size=max_size,
            scenario=scenario,
            weights=weights
        )
        
        if not composition:
            continue
        
        # Evaluate composition
        result = evaluate_composition(
            composition=composition,
            evaluators=evaluators,
            num_simulations=10  # Fixed for now, could be parameterized
        )
        
        # Check viability: must pass ALL three criteria
        # Using the spec thresholds directly
        is_viable = (
            result.mean_score >= score_threshold and
            result.variance < effective_variance_threshold and
            result.survival_probability >= survival_prob_threshold
        )
        
        if is_viable:
            viable_candidates.append((composition, result))
    
    if not viable_candidates:
        return None
    
    # Select winner: max mean_score among viable candidates
    winner_comp, winner_result = max(viable_candidates, key=lambda x: x[1].mean_score)
    
    return MonteCarloWinner(
        composition=winner_comp,
        score=winner_result.mean_score,
        variance=winner_result.variance,
        survival_probability=winner_result.survival_probability,
        num_simulations=num_samples
    )


def batch_evaluate_candidates(
    candidates: List[Dict[str, Any]],
    evaluators: Optional[List[Callable[[List[Any]], float]]] = None,
    num_simulations: int = 10
) -> Dict[str, CompositionResult]:
    """
    Evaluate multiple individual candidates (not compositions).
    
    This is useful for OpenEyes where we evaluate each fragment independently
    before assembly.
    
    Args:
        candidates: List of candidate fragments to evaluate.
        evaluators: List of evaluator functions.
        num_simulations: Number of simulations per candidate.
    
    Returns:
        Dict mapping candidate ID to CompositionResult.
    """
    results = {}
    
    for candidate in candidates:
        cand_id = candidate.get('id', hashlib.md5(str(candidate).encode()).hexdigest()[:8])
        
        # Treat single candidate as a composition of one
        result = evaluate_composition(
            composition=[candidate],
            evaluators=evaluators,
            num_simulations=num_simulations
        )
        
        results[cand_id] = result
    
    return results


# =============================================================================
# Utility Functions
# =============================================================================

def calculate_aggregate_stats(results: List[CompositionResult]) -> Dict[str, float]:
    """
    Calculate aggregate statistics across multiple evaluation results.
    
    Useful for the survival_and_weights module to determine weight adjustments.
    """
    if not results:
        return {
            'mean_mean_score': 0.0,
            'mean_variance': 0.0,
            'mean_survival_prob': 0.0,
            'total_viable': 0,
            'viability_rate': 0.0
        }
    
    mean_scores = [r.mean_score for r in results]
    variances = [r.variance for r in results]
    survival_probs = [r.survival_probability for r in results]
    viable_count = sum(1 for r in results if r.is_viable())
    
    return {
        'mean_mean_score': sum(mean_scores) / len(mean_scores),
        'mean_variance': sum(variances) / len(variances),
        'mean_survival_prob': sum(survival_probs) / len(survival_probs),
        'total_viable': viable_count,
        'viability_rate': viable_count / len(results)
    }


def get_fragment_stats(fragment_results: Dict[str, CompositionResult]) -> Dict[str, Any]:
    """
    Get statistics for a specific fragment across multiple evaluations.
    
    Args:
        fragment_results: Dict mapping fragment IDs to their CompositionResults.
    
    Returns:
        Dict with per-fragment statistics.
    """
    stats = {}
    
    for frag_id, result in fragment_results.items():
        stats[frag_id] = {
            'mean_score': result.mean_score,
            'variance': result.variance,
            'survival_probability': result.survival_probability,
            'is_viable': result.is_viable(),
            'worst_case': result.worst_case
        }
    
    return stats
