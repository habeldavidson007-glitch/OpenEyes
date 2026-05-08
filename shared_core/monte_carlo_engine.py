"""
Monte Carlo Evolution Engine — Generalized for OpenEyes and E-AR

Evaluates candidate compositions (fragment sets) under pressure scenarios.
Returns statistical metrics: mean_score, variance, survival_probability.

No domain knowledge here — purely statistical evaluation.
Domain-specific evaluators are injected at runtime.
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path


@dataclass
class CompositionResult:
    """Result of evaluating one composition."""
    mean_score: float
    variance: float
    worst_case: float
    survival_probability: float
    raw_scores: List[float] = field(default_factory=list)
    evaluator_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonteCarloWinner:
    """The winning composition after Monte Carlo evolution."""
    composition: List[Dict[str, Any]]
    mean_score: float
    variance: float
    survival_probability: float
    num_simulations: int
    reasoning_chain: Optional[Dict[str, Any]] = None


# Default thresholds (can be overridden per domain tier)
DEFAULT_THRESHOLDS = {
    "tier1": {"score": 75, "variance": 300, "survival_prob": 0.6},
    "tier2": {"score": 60, "variance": 500, "survival_prob": 0.4},
    "tier3": {"score": 45, "variance": 800, "survival_prob": 0.25},
}


def _default_evaluator(composition: List[Dict[str, Any]], 
                       scenario: Optional[Dict[str, Any]] = None,
                       domain_tier: str = "tier2") -> CompositionResult:
    """
    HYBRID DUAL-ROLL EVALUATOR for OpenEyes.
    
    Combines:
    1. Deterministic Roll (70%): Based on hard metadata (credibility, recency, consistency).
       Guarantees high-quality fragments always have a baseline score.
    2. Stochastic Roll (30%): Gaussian noise to simulate uncertainty/variance.
    
    Final Score = (0.7 * Deterministic) + (0.3 * Stochastic)
    
    Scores fragments based on:
    - Credibility class (peer_reviewed=95, guideline=90, textbook=80, etc.)
    - Recency (decay based on domain tier)
    - Reasoning chain completeness (definition + counter + latest_data)
    - Cross-source consistency (multiple sources agreeing)
    """
    import hashlib
    
    # Base credibility scores (evidence hierarchy)
    CREDIBILITY_SCORES = {
        "clinical_guideline": 95,
        "peer_reviewed_study": 90,
        "textbook": 85,
        "expert_consensus": 75,
        "government_source": 85,
        "case_report": 60,
        "news_article": 60,
        "forum": 30,
        "anecdotal": 20
    }
    
    # Recency decay rates per tier (points per year old)
    RECENCY_DECAY = {
        "tier1": 5.0,   # Medical/fast-moving: high decay
        "tier2": 2.0,   # Engineering: medium decay
        "tier3": 0.5    # Cooking/general: low decay
    }
    
    current_year = 2026
    decay_rate = RECENCY_DECAY.get(domain_tier, 2.0)
    
    # Score each fragment individually
    fragment_scores = []
    source_counts = {}  # Track unique sources
    
    for frag in composition:
        # --- DETERMINISTIC COMPONENT ---
        det_score = 0.0
        
        # 1. Credibility score (40% of det_score)
        cred_class = frag.get("credibility_class", None)
        if cred_class:
            base_cred = CREDIBILITY_SCORES.get(cred_class, 50)
        else:
            # Fallback to credibility_estimate (0-1 scale)
            base_cred = frag.get("credibility_estimate", 0.5) * 100
        det_score += base_cred * 0.4
        
        # 2. Recency score (30% of det_score)
        frag_year = frag.get("year", current_year)
        age = current_year - frag_year
        recency_score = max(0, 100 - (age * decay_rate))
        det_score += recency_score * 0.3
        
        # 3. Reasoning role bonus (30% of det_score)
        role = frag.get("reasoning_role", "definition")
        role_bonus_map = {"definition": 5, "counter_argument": 10, "latest_data": 7}
        role_bonus = role_bonus_map.get(role, 0)
        det_score += role_bonus * 0.3
        
        det_score = min(100.0, det_score)
        
        # --- STOCHASTIC COMPONENT ---
        # Use seeded random based on fragment ID for consistency
        frag_id = frag.get("fragment_id", frag.get("id", str(hash(str(frag)))))
        seed_val = int(hashlib.md5(str(frag_id).encode()).hexdigest()[:8], 16)
        rng = random.Random(seed_val)
        noise = rng.gauss(0, 5)  # Reduced standard deviation from 15 to 5 for stability
        stoch_score = det_score + noise
        stoch_score = max(0, min(100, stoch_score))
        
        # --- HYBRID COMBINATION (90/10 split for reduced variance) ---
        final_frag_score = (0.9 * det_score) + (0.1 * stoch_score)
        
        fragment_scores.append(final_frag_score)
        
        # Track sources for consistency check
        source = frag.get("source", "")
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Calculate mean fragment score
    if not fragment_scores:
        return CompositionResult(
            mean_score=0.0,
            variance=0.0,
            worst_case=0.0,
            survival_probability=0.0,
            raw_scores=[0.0] * 20,
            evaluator_details={"error": "no_fragments"}
        )
    
    mean_frag_score = sum(fragment_scores) / len(fragment_scores)
    
    # 4. Reasoning chain completeness bonus
    has_definition = any(f.get("reasoning_role") == "definition" for f in composition)
    has_counter = any(f.get("reasoning_role") == "counter_argument" for f in composition)
    has_latest = any(f.get("reasoning_role") == "latest_data" for f in composition)
    
    chain_bonus = 0
    if has_definition:
        chain_bonus += 5
    if has_counter:
        chain_bonus += 10  # Critical for tier1
    if has_latest:
        chain_bonus += 7
    
    # 5. Cross-source consistency bonus
    num_sources = len(source_counts)
    consistency_bonus = min(10, (num_sources - 1) * 3)  # Max 10 points
    
    # Final score
    final_score = mean_frag_score + chain_bonus + consistency_bonus
    final_score = max(0, min(100, final_score))  # Clamp to [0, 100]
    
    # Generate simulation scores with reduced variance for stability
    # Variance represents uncertainty in the knowledge, not randomness
    uncertainty = 5.0 if len(composition) < 2 else 3.0
    if domain_tier == "tier1" and not has_counter:
        uncertainty = 12.0  # Moderate uncertainty without counter-argument
    
    num_simulations = 20
    scores = [final_score + random.gauss(0, uncertainty) for _ in range(num_simulations)]
    scores = [max(0, min(100, s)) for s in scores]
    
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    worst_case = min(scores)
    
    threshold = DEFAULT_THRESHOLDS[domain_tier]["score"]
    survival_probability = sum(1 for s in scores if s >= threshold) / len(scores)
    
    return CompositionResult(
        mean_score=mean_score,
        variance=variance,
        worst_case=worst_case,
        survival_probability=survival_probability,
        raw_scores=scores,
        evaluator_details={
            "mean_fragment_score": mean_frag_score,
            "chain_bonus": chain_bonus,
            "consistency_bonus": consistency_bonus,
            "has_definition": has_definition,
            "has_counter_argument": has_counter,
            "has_latest_data": has_latest,
            "num_sources": num_sources,
            "domain_tier": domain_tier,
            "recency_decay_applied": decay_rate,
            "hybrid_evaluator": True,
            "deterministic_weight": 0.9,
            "stochastic_weight": 0.1
        }
    )


def generate_composition(primitives: List[Dict[str, Any]], 
                        min_size: int = 1,
                        max_size: int = 5,
                        scenario: Optional[Dict[str, Any]] = None,
                        weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    """
    Generate one candidate composition from weighted primitives/fragments.
    
    Args:
        primitives: Pool of available fragments/primitives
        min_size: Minimum number of items in composition
        max_size: Maximum number of items in composition
        scenario: Optional scenario with expected_constructs/fragments
        weights: Optional weight dict for biased selection
    
    Returns:
        List of selected primitives (the composition)
    """
    if not primitives:
        return []
    
    # Determine composition size
    size = random.randint(min_size, min(max_size, len(primitives)))
    
    # Build weighted pool
    if weights:
        weighted_pool = []
        for prim in primitives:
            prim_id = prim.get("id", str(hash(str(prim))))
            weight = weights.get(prim_id, 1.0)
            # Boost weight if scenario expects this construct/fragment
            if scenario and "expected_fragments" in scenario:
                tags = prim.get("tags", [])
                if any(tag in scenario["expected_fragments"] for tag in tags):
                    weight *= 1.5
            weighted_pool.extend([prim] * max(1, int(weight * 10)))
    else:
        weighted_pool = primitives
    
    # Select without replacement
    composition = []
    used_ids = set()
    
    attempts = 0
    while len(composition) < size and attempts < size * 10:
        candidate = random.choice(weighted_pool)
        cand_id = candidate.get("id", str(hash(str(candidate))))
        
        if cand_id not in used_ids:
            composition.append(candidate)
            used_ids.add(cand_id)
        
        attempts += 1
    
    return composition


def evaluate_composition(composition: List[Dict[str, Any]],
                        evaluator: Optional[Callable] = None,
                        scenario: Optional[Dict[str, Any]] = None,
                        domain_tier: str = "tier2") -> CompositionResult:
    """
    Evaluate one composition using the provided evaluator.
    
    Args:
        composition: List of fragments/primitives to evaluate
        evaluator: Function(composition, scenario) -> CompositionResult
                  If None, uses default evaluator
        scenario: Optional scenario context
        domain_tier: "tier1", "tier2", or "tier3"
    
    Returns:
        CompositionResult with statistical metrics
    """
    if evaluator is None:
        evaluator = lambda c, s, t: _default_evaluator(c, s, t)
    
    try:
        result = evaluator(composition, scenario, domain_tier)
        if isinstance(result, CompositionResult):
            return result
        else:
            # Fallback if evaluator returns dict
            return CompositionResult(**result)
    except Exception as e:
        # Return low-score result on evaluator error
        return CompositionResult(
            mean_score=10.0,
            variance=1000.0,
            worst_case=5.0,
            survival_probability=0.0,
            raw_scores=[10.0],
            evaluator_details={"error": str(e)}
        )


def monte_carlo_evolve(primitives: List[Dict[str, Any]],
                      num_samples: int = 50,
                      stability_threshold: float = 0.3,
                      survival_threshold: float = 0.7,
                      scenario: Optional[Dict[str, Any]] = None,
                      evaluator: Optional[Callable] = None,
                      domain_tier: str = "tier2",
                      weights: Optional[Dict[str, float]] = None) -> Optional[MonteCarloWinner]:
    """
    Full Monte Carlo evolution loop.
    
    Generates N candidate compositions, evaluates each, filters by survival
    criteria, and returns the best surviving candidate.
    
    Args:
        primitives: Pool of available fragments/primitives
        num_samples: Number of compositions to generate and evaluate
        stability_threshold: Maximum acceptable variance (normalized 0-1)
        survival_threshold: Minimum survival probability
        scenario: Optional scenario context
        evaluator: Domain-specific evaluator function
        domain_tier: "tier1", "tier2", or "tier3"
        weights: Optional fragment weights for biased selection
    
    Returns:
        MonteCarloWinner if any composition survives, else None
    """
    if not primitives:
        return None
    
    thresholds = DEFAULT_THRESHOLDS.get(domain_tier, DEFAULT_THRESHOLDS["tier2"])
    variance_max = thresholds["variance"]
    survival_min = thresholds["survival_prob"]
    
    viable_candidates = []
    
    for i in range(num_samples):
        # Generate candidate composition
        composition = generate_composition(
            primitives=primitives,
            min_size=1,
            max_size=min(5, len(primitives)),
            scenario=scenario,
            weights=weights
        )
        
        if not composition:
            continue
        
        # Evaluate composition
        result = evaluate_composition(
            composition=composition,
            evaluator=evaluator,
            scenario=scenario,
            domain_tier=domain_tier
        )
        
        # Check survival criteria
        if result.variance < variance_max and result.survival_probability >= survival_min:
            viable_candidates.append({
                "composition": composition,
                "result": result
            })
    
    if not viable_candidates:
        return None
    
    # Select winner: highest mean score among viable candidates
    winner = max(viable_candidates, key=lambda x: x["result"].mean_score)
    
    return MonteCarloWinner(
        composition=winner["composition"],
        mean_score=winner["result"].mean_score,
        variance=winner["result"].variance,
        survival_probability=winner["result"].survival_probability,
        num_simulations=num_samples,
        reasoning_chain=_extract_reasoning_chain(winner["composition"])
    )


def _extract_reasoning_chain(composition: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract and structure the reasoning chain from a composition."""
    definition = None
    counter_arguments = []
    latest_data = None
    
    for fragment in composition:
        role = fragment.get("reasoning_role")
        if role == "definition":
            definition = fragment
        elif role == "counter_argument":
            counter_arguments.append(fragment)
        elif role == "latest_data":
            if latest_data is None or fragment.get("year", 0) > latest_data.get("year", 0):
                latest_data = fragment
    
    if not definition and not counter_arguments and not latest_data:
        return None
    
    return {
        "definition": definition,
        "counter_arguments": counter_arguments,
        "latest_data": latest_data,
        "completeness_score": sum([
            1 if definition else 0,
            min(len(counter_arguments), 3) * 0.33,
            1 if latest_data else 0
        ]) / 3.0
    }


def batch_evaluate(primitives: List[Dict[str, Any]],
                  scenarios: List[Dict[str, Any]],
                  evaluator: Optional[Callable] = None,
                  domain_tier: str = "tier2") -> Dict[str, List[MonteCarloWinner]]:
    """
    Run Monte Carlo evolution across multiple scenarios.
    
    Returns dict mapping scenario_id to list of winners (may have multiple per scenario).
    """
    results = {}
    
    for scenario in scenarios:
        scenario_id = scenario.get("id", "unknown")
        winner = monte_carlo_evolve(
            primitives=primitives,
            scenario=scenario,
            evaluator=evaluator,
            domain_tier=domain_tier
        )
        
        if winner:
            results[scenario_id] = [winner]
        else:
            results[scenario_id] = []
    
    return results


def get_aggregate_stats(winners: List[MonteCarloWinner]) -> Dict[str, float]:
    """Calculate aggregate statistics across multiple winners."""
    if not winners:
        return {"mean_score": 0, "mean_variance": 0, "mean_survival": 0, "count": 0}
    
    return {
        "mean_score": sum(w.mean_score for w in winners) / len(winners),
        "mean_variance": sum(w.variance for w in winners) / len(winners),
        "mean_survival": sum(w.survival_probability for w in winners) / len(winners),
        "count": len(winners),
        "best_score": max(w.mean_score for w in winners),
        "worst_score": min(w.mean_score for w in winners)
    }


def analyze_fragment_performance(fragments: List[Dict[str, Any]], 
                                winners: List[MonteCarloWinner]) -> List[Dict[str, Any]]:
    """
    Analyze how often each fragment appears in winning compositions.
    
    Returns list of fragments with added 'win_rate' and 'avg_score_when_won' fields.
    """
    fragment_stats = {}
    
    for fragment in fragments:
        fid = fragment.get("id", str(hash(str(fragment))))
        fragment_stats[fid] = {
            "fragment": fragment,
            "appearances": 0,
            "total_score": 0.0
        }
    
    for winner in winners:
        for fragment in winner.composition:
            fid = fragment.get("id", str(hash(str(fragment))))
            if fid in fragment_stats:
                fragment_stats[fid]["appearances"] += 1
                fragment_stats[fid]["total_score"] += winner.mean_score
    
    results = []
    for fid, stats in fragment_stats.items():
        fragment = stats["fragment"].copy()
        if stats["appearances"] > 0:
            fragment["win_rate"] = stats["appearances"] / len(winners)
            fragment["avg_score_when_won"] = stats["total_score"] / stats["appearances"]
        else:
            fragment["win_rate"] = 0.0
            fragment["avg_score_when_won"] = 0.0
        results.append(fragment)
    
    return sorted(results, key=lambda x: x["win_rate"], reverse=True)
