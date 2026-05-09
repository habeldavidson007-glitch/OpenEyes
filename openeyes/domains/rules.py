from __future__ import annotations

DOMAIN_THRESHOLDS = {
    "medical": {"tier": 1, "min_score": 70.0, "require_counter": True},
    "engineering": {"tier": 2, "min_score": 62.0, "require_counter": False},
    "legal": {"tier": 1, "min_score": 72.0, "require_counter": True},
    "cooking": {"tier": 3, "min_score": 45.0, "require_counter": False},
    "trading": {"tier": 2, "min_score": 65.0, "require_counter": True},
    "investment": {"tier": 2, "min_score": 65.0, "require_counter": True},
}
