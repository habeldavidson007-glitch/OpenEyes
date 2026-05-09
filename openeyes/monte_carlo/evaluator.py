from __future__ import annotations

import numpy as np

from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.hierarchies import get_credibility_score


def dual_roll_score(domain: str, fragments: list[Fragment], gaussian_noise: np.ndarray) -> np.ndarray:
    if not fragments:
        return np.zeros_like(gaussian_noise)
    cred = np.array([get_credibility_score(domain, f.source_type) for f in fragments], dtype=float).mean()
    weight = np.array([f.effective_weight for f in fragments], dtype=float).mean() * 100.0
    base = 0.6 * cred + 0.4 * weight
    return np.clip(base + gaussian_noise * 4.0, 0.0, 100.0)
