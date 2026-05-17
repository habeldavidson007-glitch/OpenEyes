from __future__ import annotations

import numpy as np

from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.hierarchies import get_credibility_score


def dual_roll_score(domain: str, fragments: list, gaussian_noise: np.ndarray) -> np.ndarray:
    """
    Calculate dual-roll Monte Carlo scores for fragments.
    
    Args:
        domain: The domain code (e.g., 'eco', 'hc')
        fragments: List of Fragment objects or RetrievalRecord objects with fragment attribute
        gaussian_noise: Pre-generated noise array
        
    Returns:
        numpy array of scores
    """
    if not fragments:
        return np.zeros_like(gaussian_noise)
    
    # Handle both Fragment objects and RetrievalRecord objects
    def get_fragment_source_type(f):
        if hasattr(f, 'source_type'):
            return f.source_type
        elif hasattr(f, 'fragment') and hasattr(f.fragment, 'source_type'):
            return f.fragment.source_type
        else:
            return "peer_reviewed_study"  # default
    
    def get_fragment_weight(f):
        if hasattr(f, 'effective_weight'):
            return f.effective_weight
        elif hasattr(f, 'fragment') and hasattr(f.fragment, 'effective_weight'):
            return f.fragment.effective_weight
        elif hasattr(f, 'success_rate_ema'):
            return f.success_rate_ema
        elif hasattr(f, 'fragment') and hasattr(f.fragment, 'success_rate_ema'):
            return f.fragment.success_rate_ema
        else:
            return 0.7  # default
    
    cred = np.array([get_credibility_score(domain, get_fragment_source_type(f)) for f in fragments], dtype=float).mean()
    weight = np.array([get_fragment_weight(f) for f in fragments], dtype=float).mean() * 100.0
    base = 0.6 * cred + 0.4 * weight
    # FIX 2: Reduce noise magnitude from 4.0 to 2.0 for better discrimination
    return np.clip(base + gaussian_noise * 2.0, 0.0, 100.0)
