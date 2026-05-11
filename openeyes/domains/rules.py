from __future__ import annotations

# FIX 2: Updated DOMAIN_THRESHOLDS with mean_score >= 65 AND variance < 300 AND survival_probability >= 0.55
DOMAIN_THRESHOLDS = {
    "medical": {"tier": 1, "min_score": 70.0, "require_counter": True},
    "engineering": {"tier": 2, "min_score": 62.0, "require_counter": False},
    "legal": {"tier": 1, "min_score": 72.0, "require_counter": True},
    "cooking": {"tier": 3, "min_score": 45.0, "require_counter": False},
    "trading": {"tier": 2, "min_score": 65.0, "require_counter": True},
    "investment": {"tier": 2, "min_score": 65.0, "require_counter": True},
}

# FIX 2: Tighter survival thresholds for Monte Carlo evaluation
# These require mean_score >= 65 AND variance < 300 AND survival_probability >= 0.55
SURVIVAL_THRESHOLDS = {
    "tier1": {"min_score": 65, "max_variance": 300, "min_survival_prob": 0.55},
    "tier2": {"min_score": 65, "max_variance": 300, "min_survival_prob": 0.55},
    "tier3": {"min_score": 65, "max_variance": 300, "min_survival_prob": 0.55},
}
