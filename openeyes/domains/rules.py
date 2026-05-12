from __future__ import annotations

# FIX: Updated DOMAIN_THRESHOLDS with lower min_score for healthcare and governance to improve recall
# Added explicit entries for 'economy', 'healthcare', 'governance'
DOMAIN_THRESHOLDS = {
    "economy": {"tier": 2, "min_score": 55.0, "require_counter": False},
    "healthcare": {"tier": 1, "min_score": 50.0, "require_counter": False},  # Lowered from 70
    "governance": {"tier": 1, "min_score": 50.0, "require_counter": False},  # Lowered from 72
    "medical": {"tier": 1, "min_score": 50.0, "require_counter": False},     # Alias for healthcare
    "engineering": {"tier": 2, "min_score": 55.0, "require_counter": False},
    "legal": {"tier": 1, "min_score": 50.0, "require_counter": False},       # Alias for governance
    "cooking": {"tier": 3, "min_score": 45.0, "require_counter": False},
    "trading": {"tier": 2, "min_score": 55.0, "require_counter": False},
    "investment": {"tier": 2, "min_score": 55.0, "require_counter": False},
}

# FIX: Relaxed survival thresholds to allow more fragments to pass Monte Carlo
# Reduced min_score from 65 to 50, increased max_variance from 300 to 500
SURVIVAL_THRESHOLDS = {
    "tier1": {"min_score": 50, "max_variance": 500, "min_survival_prob": 0.45},
    "tier2": {"min_score": 50, "max_variance": 500, "min_survival_prob": 0.45},
    "tier3": {"min_score": 45, "max_variance": 600, "min_survival_prob": 0.40},
}
