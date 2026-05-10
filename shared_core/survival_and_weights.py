"""
Survival and Weights Module for OpenEyes

Generalized from E-AR's evolution/survival.py.
This module knows nothing about OpenEyes or E-AR specifically.
It operates on abstract candidates, weights, and scores.
Domain meaning is injected by the calling layer.

For OpenEyes: The gene pool will store knowledge fragment weights,
not E+ primitive weights. Fragment IDs should be stable, content-addressable
identifiers (e.g., hash of source + content), not sequential integers.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# Configuration
# =============================================================================

ROOT = Path(__file__).resolve().parent.parent
GENE_POOL = ROOT / "evolution_data" / "gene_pool.json"

# Default thresholds (matching monte_carlo_engine.py)
DEFAULT_SCORE_THRESHOLD = 60
DEFAULT_VARIANCE_THRESHOLD = 500
DEFAULT_SURVIVAL_PROB_THRESHOLD = 0.4

# Weight adjustment rules (active per spec)
SURVIVED_BASE_ADJUSTMENT = 0.05
SURVIVED_HIGH_STABILITY_BONUS = 0.02
SURVIVED_HIGH_SURVIVAL_PROB_BONUS = 0.02

FAILED_BASE_PENALTY = 0.03
FAILED_HIGH_VARIANCE_PENALTY = 0.02
FAILED_LOW_SURVIVAL_PROB_PENALTY = 0.02

WEIGHT_MIN = 0.1
WEIGHT_MAX = 2.0


# =============================================================================
# Gene Pool I/O
# =============================================================================

def load_gene_pool() -> Dict[str, Any]:
    """
    Load the gene pool from disk.
    
    Returns:
        Dict mapping fragment/primitive IDs to their data including weights.
        Returns empty dict if file doesn't exist.
    """
    if not GENE_POOL.exists():
        return {}
    
    try:
        with open(GENE_POOL, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_gene_pool(pool: Dict[str, Any]) -> None:
    """
    Save the gene pool to disk.
    
    Args:
        pool: Dict mapping fragment/primitive IDs to their data.
    """
    # Ensure directory exists
    GENE_POOL.parent.mkdir(parents=True, exist_ok=True)
    
    with open(GENE_POOL, "w") as f:
        json.dump(pool, f, indent=2)


# =============================================================================
# Core Survival Logic
# =============================================================================

def survives_mc(
    score: float,
    selected: List[Dict[str, Any]],
    variance: float,
    survival_probability: float,
    aggregate_stats: Optional[Dict[str, Any]] = None,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    survival_prob_threshold: float = DEFAULT_SURVIVAL_PROB_THRESHOLD
) -> Dict[str, Any]:
    """
    Enhanced survival logic for Monte Carlo evolution.
    
    Survival criteria (must pass ALL three):
    1. Mean score >= threshold (default: 60)
    2. Variance < threshold (default: 500 for 5-evaluator diversity)
    3. Survival probability >= threshold (default: 0.4)
    
    Weight adjustment rules:
    - Survived:
      - base adjustment: +0.05
      - high stability bonus (variance < threshold/2): +0.02 extra
      - high survival prob (≥ 0.9): +0.02 extra
    - Failed:
      - base penalty: -0.03
      - high variance penalty: -0.02 extra
      - low survival prob (< 0.5): -0.02 extra
    
    All weights clamped to [0.1, 2.0]
    
    Args:
        score: Mean score from Monte Carlo evaluation
        selected: List of selected primitives/fragments
        variance: Variance across evaluator scores (stability metric)
        survival_probability: Probability of scoring above threshold
        aggregate_stats: Aggregate statistics from Monte Carlo run (optional)
        score_threshold: Minimum mean score required (default: 60)
        variance_threshold: Maximum acceptable variance (default: 500)
        survival_prob_threshold: Minimum survival probability (default: 0.4)
    
    Returns:
        Dict with survival decision and metadata:
        {
            "passed": bool,
            "criteria": { "score_ok": bool, "stability_ok": bool, "probability_ok": bool },
            "metrics": { "score": float, "variance": float, "survival_probability": float },
            "thresholds": { ... },
            "gene_pool_updated": bool
        }
    """
    # Check all three criteria
    score_ok = score >= score_threshold
    stability_ok = variance < variance_threshold
    probability_ok = survival_probability >= survival_prob_threshold
    
    # Must pass all criteria to survive
    passed = score_ok and stability_ok and probability_ok
    
    # Update gene pool weights
    pool = load_gene_pool()
    
    for primitive in selected:
        # Convert FragmentCandidate or Fragment object to dict if needed
        if hasattr(primitive, 'to_dict'):
            prim_dict = primitive.to_dict()
        else:
            prim_dict = primitive
        
        pid = str(prim_dict.get("id", ""))
        
        if not pid:
            continue
        
        if pid not in pool:
            # Initialize new entry with primitive data
            pool[pid] = prim_dict.copy()
            pool[pid]["weight"] = pool[pid].get("weight", 1.0)
        
        current = pool[pid]["weight"]
        
        # Adjust weight based on performance
        if passed:
            # Strong performance: boost weight
            adjustment = SURVIVED_BASE_ADJUSTMENT
            
            # Extra boost for high stability
            if variance < variance_threshold * 0.5:
                adjustment += SURVIVED_HIGH_STABILITY_BONUS
            
            # Extra boost for high survival probability
            if survival_probability >= 0.9:
                adjustment += SURVIVED_HIGH_SURVIVAL_PROB_BONUS
            
            current += adjustment
        else:
            # Weak performance: reduce weight
            adjustment = FAILED_BASE_PENALTY
            
            # Extra penalty for high variance (unstable)
            if variance >= variance_threshold:
                adjustment += FAILED_HIGH_VARIANCE_PENALTY
            
            # Extra penalty for low survival probability
            if survival_probability < 0.5:
                adjustment += FAILED_LOW_SURVIVAL_PROB_PENALTY
            
            current -= adjustment
        
        # Clamp weight to valid range
        current = max(WEIGHT_MIN, min(current, WEIGHT_MAX))
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
            "score": round(score, 2),
            "variance": round(variance, 2),
            "survival_probability": round(survival_probability, 2)
        },
        "thresholds": {
            "score_threshold": score_threshold,
            "variance_threshold": variance_threshold,
            "survival_prob_threshold": survival_prob_threshold
        },
        "gene_pool_updated": True
    }


def survives(
    score: float,
    selected: List[Dict[str, Any]],
    score_threshold: float = DEFAULT_SCORE_THRESHOLD
) -> bool:
    """
    Simple survival check based on score only.
    
    Legacy function for backward compatibility. Use survives_mc() for
    full Monte Carlo survival logic.
    
    Args:
        score: Mean score from evaluation
        selected: List of selected primitives/fragments
        score_threshold: Minimum score to survive (default: 60)
    
    Returns:
        True if score meets threshold, False otherwise
    """
    passed = score >= score_threshold
    
    # Update weights (simple version)
    pool = load_gene_pool()
    
    for primitive in selected:
        pid = str(primitive.get("id", ""))
        
        if not pid:
            continue
        
        if pid not in pool:
            pool[pid] = primitive.copy()
            pool[pid]["weight"] = pool[pid].get("weight", 1.0)
        
        current = pool[pid]["weight"]
        
        if passed:
            current += SURVIVED_BASE_ADJUSTMENT
        else:
            current -= FAILED_BASE_PENALTY
        
        current = max(WEIGHT_MIN, min(current, WEIGHT_MAX))
        pool[pid]["weight"] = round(current, 2)
    
    save_gene_pool(pool)
    
    return passed


def evolve_weights(
    selected: List[Dict[str, Any]],
    survived: bool
) -> None:
    """
    Evolve weights for selected primitives/fragments based on survival outcome.
    
    This is a lower-level function used by survives() and survives_mc().
    Direct usage is not recommended unless implementing custom survival logic.
    
    Args:
        selected: List of selected primitives/fragments
        survived: Whether the selection survived evaluation
    """
    pool = load_gene_pool()
    
    for primitive in selected:
        pid = str(primitive.get("id", ""))
        
        if not pid:
            continue
        
        if pid not in pool:
            pool[pid] = primitive.copy()
            pool[pid]["weight"] = pool[pid].get("weight", 1.0)
        
        current = pool[pid]["weight"]
        
        if survived:
            current += SURVIVED_BASE_ADJUSTMENT
        else:
            current -= FAILED_BASE_PENALTY
        
        current = max(WEIGHT_MIN, min(current, WEIGHT_MAX))
        pool[pid]["weight"] = round(current, 2)
    
    save_gene_pool(pool)


# =============================================================================
# Utility Functions
# =============================================================================

def get_weight(primitive_id: str, default: float = 1.0) -> float:
    """
    Get the current weight for a primitive/fragment.
    
    Args:
        primitive_id: ID of the primitive/fragment
        default: Default weight if not found in gene pool
    
    Returns:
        Current weight or default if not found
    """
    pool = load_gene_pool()
    
    if primitive_id in pool:
        return pool[primitive_id].get("weight", default)
    
    return default


def reset_weights() -> None:
    """
    Reset all weights to default value (1.0).
    
    Warning: This clears all evolved weight data. Use with caution.
    """
    pool = load_gene_pool()
    
    for pid in pool:
        pool[pid]["weight"] = 1.0
    
    save_gene_pool(pool)


def get_gene_pool_stats() -> Dict[str, Any]:
    """
    Get statistics about the current gene pool.
    
    Returns:
        Dict with gene pool statistics
    """
    pool = load_gene_pool()
    
    if not pool:
        return {
            "total_entries": 0,
            "mean_weight": 0.0,
            "min_weight": 0.0,
            "max_weight": 0.0,
            "entries": {}
        }
    
    weights = [entry.get("weight", 1.0) for entry in pool.values()]
    
    return {
        "total_entries": len(pool),
        "mean_weight": round(sum(weights) / len(weights), 2) if weights else 0.0,
        "min_weight": round(min(weights), 2) if weights else 0.0,
        "max_weight": round(max(weights), 2) if weights else 0.0,
        "entries": {k: v.get("weight", 1.0) for k, v in pool.items()}
    }
