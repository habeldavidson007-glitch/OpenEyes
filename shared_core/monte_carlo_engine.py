import random
from evolution.primitive_registry import load_primitives
from evolution.compatibility_matrix import is_compatible
from core.pressure import evaluate_all

def generate_composition(primitives, min_size=3, max_size=7, scenario=None):
    """
    Generate a single composition of compatible primitives.
    
    Args:
        primitives: List of available primitives
        min_size: Minimum composition size
        max_size: Maximum composition size
        scenario: Optional scenario dict that influences selection
    
    Returns:
        List of selected primitives forming a composition
    """
    size = random.randint(min_size, max_size)
    composition = []
    available = primitives[:]
    
    # If scenario has expected constructs, boost weights for matching primitives
    if scenario and "expected_constructs" in scenario:
        expected = scenario.get("expected_constructs", [])
        for p in available:
            tags = p.get("tags", [])
            # Boost weight if primitive matches expected constructs
            if any(tag in expected for tag in tags):
                p["weight"] = p.get("weight", 1.0) * 1.5  # 50% boost
    
    while len(composition) < size and available:
        if not composition:
            # First primitive: weighted selection
            weights = [p["weight"] for p in available]
            chosen = random.choices(available, weights=weights, k=1)[0]
        else:
            # Subsequent primitives: must be compatible with at least one existing
            compatible = [
                p for p in available
                if any(is_compatible(p, existing) for existing in composition)
            ]
            
            if not compatible:
                # No compatible primitives left, stop early
                break
            
            weights = [p["weight"] for p in compatible]
            chosen = random.choices(compatible, weights=weights, k=1)[0]
        
        composition.append(chosen)
        available.remove(chosen)
    
    return composition


def evaluate_composition(composition):
    """Evaluate a composition and return detailed statistics."""
    pressure_result = evaluate_all(composition)
    
    scores = pressure_result.get("individual_scores", [])
    if not scores:
        # Fallback: extract from simulator results
        for result in pressure_result["simulators"]:
            for key, value in result.items():
                if key.endswith("_score"):
                    scores.append(value)
    
    mean_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate variance (stability metric)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores) if scores else 0
    
    # Calculate worst-case (risk metric)
    worst_case = min(scores) if scores else 0
    
    # Calculate survival probability (P(score > 60))
    threshold = 60
    above_threshold = sum(1 for s in scores if s > threshold)
    survival_prob = above_threshold / len(scores) if scores else 0
    
    return {
        "composition": composition,
        "mean_score": round(mean_score, 2),
        "variance": round(variance, 2),
        "worst_case": round(worst_case, 2),
        "survival_probability": round(survival_prob, 2),
        "simulator_scores": scores,
        "pressure_result": pressure_result
    }


def monte_carlo_evolve(num_samples=50, stability_threshold=0.3, survival_threshold=0.7, scenario=None):
    """
    Run Monte Carlo evolution with multiple candidate compositions.
    
    Args:
        num_samples: Number of candidate compositions to sample
        stability_threshold: Maximum acceptable variance (lower = more stable)
        survival_threshold: Minimum survival probability required
        scenario: Optional scenario dict to guide composition generation
    
    Returns:
        Best composition based on distributional stability and score
    """
    primitives = load_primitives()
    candidates = []
    
    # Generate and evaluate N candidate compositions
    for _ in range(num_samples):
        composition = generate_composition(primitives, scenario=scenario)
        if len(composition) >= 2:  # Ensure minimum viable composition
            evaluation = evaluate_composition(composition)
            candidates.append(evaluation)
    
    if not candidates:
        # Fallback: generate at least one composition
        composition = generate_composition(primitives)
        return evaluate_composition(composition)
    
    # Filter by stability constraint (variance < threshold)
    stable_candidates = [
        c for c in candidates
        if c["variance"] < stability_threshold * 100  # Scale threshold appropriately
    ]
    
    # If no stable candidates, relax constraint
    if not stable_candidates:
        stable_candidates = sorted(candidates, key=lambda x: x["variance"])[:max(1, len(candidates) // 4)]
    
    # Filter by survival probability constraint
    viable_candidates = [
        c for c in stable_candidates
        if c["survival_probability"] >= survival_threshold
    ]
    
    # If no viable candidates, relax constraint
    if not viable_candidates:
        viable_candidates = sorted(
            stable_candidates,
            key=lambda x: x["survival_probability"],
            reverse=True
        )[:max(1, len(stable_candidates) // 2)]
    
    # Select winner: highest mean score among viable candidates
    winner = max(viable_candidates, key=lambda x: x["mean_score"])
    
    # Calculate aggregate statistics across all samples
    all_scores = [c["mean_score"] for c in candidates]
    aggregate_stats = {
        "total_samples": num_samples,
        "stable_samples": len(stable_candidates),
        "viable_samples": len(viable_candidates),
        "best_score": winner["mean_score"],
        "average_score": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
        "score_distribution": {
            "min": round(min(all_scores), 2) if all_scores else 0,
            "max": round(max(all_scores), 2) if all_scores else 0,
            "std_dev": round(
                (sum((s - sum(all_scores)/len(all_scores))**2 for s in all_scores) / len(all_scores)) ** 0.5,
                2
            ) if all_scores else 0
        }
    }
    
    return {
        **winner,
        "aggregate_stats": aggregate_stats,
        "all_candidates_evaluated": len(candidates)
    }
