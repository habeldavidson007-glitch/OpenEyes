import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GENE_POOL = ROOT / "evolution_data" / "gene_pool.json"


def load_gene_pool():
    if not GENE_POOL.exists():
        return {}

    with open(GENE_POOL, "r") as f:
        return json.load(f)


def save_gene_pool(pool):
    with open(GENE_POOL, "w") as f:
        json.dump(pool, f, indent=2)


def evolve_weights(selected, survived):
    pool = load_gene_pool()

    for primitive in selected:
        pid = str(primitive["id"])

        if pid not in pool:
            pool[pid] = primitive

        current = pool[pid]["weight"]

        if survived:
            current += 0.05
        else:
            current -= 0.03

        current = max(0.1, min(current, 2.0))

        pool[pid]["weight"] = round(current, 2)

    save_gene_pool(pool)


def survives(score, selected):
    passed = score >= 60

    evolve_weights(selected, passed)

    return passed


def survives_mc(score, selected, variance, survival_probability, aggregate_stats, 
                score_threshold=60, variance_threshold=500, survival_prob_threshold=0.4):
    """
    Enhanced survival logic for Monte Carlo evolution.
    
    Survival criteria:
    1. Mean score >= threshold
    2. Variance < threshold (stability requirement) - set to 500 for 5-simulator swarm
    3. Survival probability >= threshold - relaxed to 0.4
    
    Note: With 5 simulators producing diverse scores (beginner=95, maintainer=50, 
    runtime=100, scaler=60, teacher=50), typical variance is ~484. Threshold set
    to 500 to allow natural simulator diversity while still catching extreme instability.
    
    Args:
        score: Mean score from Monte Carlo evaluation
        selected: List of selected primitives
        variance: Variance across simulator scores (stability metric)
        survival_probability: Probability of scoring above threshold
        aggregate_stats: Aggregate statistics from Monte Carlo run
        score_threshold: Minimum mean score required
        variance_threshold: Maximum acceptable variance (500 for 5-simulator diversity)
        survival_prob_threshold: Minimum survival probability (relaxed to 0.4)
    
    Returns:
        dict with survival decision and metadata
    """
    # Check all three criteria
    score_ok = score >= score_threshold
    stability_ok = variance < variance_threshold
    probability_ok = survival_probability >= survival_prob_threshold
    
    # Must pass all criteria to survive
    passed = score_ok and stability_ok and probability_ok
    
    # Calculate weight adjustment based on performance
    pool = load_gene_pool()
    
    for primitive in selected:
        pid = str(primitive["id"])
        
        if pid not in pool:
            pool[pid] = primitive.copy()
        
        current = pool[pid]["weight"]
        
        # Adjust weight based on multiple factors
        if passed:
            # Strong performance: boost weight
            adjustment = 0.05
            
            # Extra boost for high stability
            if variance < variance_threshold * 0.5:
                adjustment += 0.02
            
            # Extra boost for high survival probability
            if survival_probability >= 0.9:
                adjustment += 0.02
            
            current += adjustment
        else:
            # Weak performance: reduce weight
            adjustment = 0.03
            
            # Extra penalty for high variance (unstable)
            if variance >= variance_threshold:
                adjustment += 0.02
            
            # Extra penalty for low survival probability
            if survival_probability < 0.5:
                adjustment += 0.02
            
            current -= adjustment
        
        # Clamp weight to valid range
        current = max(0.1, min(current, 2.0))
        pool[pid]["weight"] = round(current, 2)
    
    save_gene_pool(pool)
    
    return {
        "passed": passed,
        "criteria": {
            "score_ok": score_ok,
            "stability_ok": stability_ok,
            "probability_ok": probability_ok
        },
        "metrics": {
            "score": score,
            "variance": variance,
            "survival_probability": survival_probability
        },
        "thresholds": {
            "score_threshold": score_threshold,
            "variance_threshold": variance_threshold,
            "survival_prob_threshold": survival_prob_threshold
        },
        "gene_pool_updated": True
    }
