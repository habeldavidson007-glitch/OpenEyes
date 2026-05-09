from __future__ import annotations

import numpy as np
from scipy.stats import variation

from openeyes.core.decomposition import decompose_query
from openeyes.domains.rules import DOMAIN_THRESHOLDS
from openeyes.knowledge.fragments import Fragment
from openeyes.monte_carlo.evaluator import dual_roll_score
from openeyes.monte_carlo.rng import PCG64, box_muller, sobol_vectors


class MonteCarloEngine:
    def run(self, query: str, domain: str, fragments: list[Fragment]) -> dict:
        _ = decompose_query(query)
        agents = 1000
        pcg = PCG64(seed=abs(hash((query, domain))) % (2**32))
        sobol = sobol_vectors(agents, dim=2)
        noise = box_muller(pcg.random(agents), sobol[:, 1])
        scores = dual_roll_score(domain, fragments, noise)
        for _ in range(4):
            if variation(scores) < 0.02:
                break
            scores = 0.9 * scores + 0.1 * dual_roll_score(domain, fragments, box_muller(pcg.random(agents), pcg.random(agents)))
        th = DOMAIN_THRESHOLDS.get(domain, {"min_score": 60.0, "require_counter": False})
        confidence = float(np.mean(scores))
        has_counter = any(f.limitations for f in fragments)
        ok = confidence >= th["min_score"] and (not th.get("require_counter") or has_counter)
        return {"confidence": round(confidence, 2), "ok": ok}
