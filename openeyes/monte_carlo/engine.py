from __future__ import annotations

import hashlib
import json

import numpy as np
from scipy.stats import variation

from openeyes.core.decomposition import decompose_query
from openeyes.domains.rules import DOMAIN_THRESHOLDS
from openeyes.knowledge.fragments import Fragment
from openeyes.monte_carlo.evaluator import dual_roll_score
from openeyes.monte_carlo.rng import PCG64, box_muller, sobol_vectors


class MonteCarloEngine:
    @staticmethod
    def stable_seed(query: str, domain: str) -> int:
        digest = hashlib.sha256(f"{domain}::{query}".encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big") % (2**32)

    def run(self, query: str, domain: str, fragments: list[Fragment]) -> dict:
        sub_questions = decompose_query(query)
        agents = 1024  # power-of-two for Sobol balance
        seed = self.stable_seed(query, domain)
        pcg = PCG64(seed=seed)
        sobol = sobol_vectors(agents, dim=2)
        noise = box_muller(pcg.random(agents), sobol[:, 1])
        scores = dual_roll_score(domain, fragments, noise)

        converged = False
        for _ in range(16):
            if variation(scores) < 0.05:
                converged = True
                break
            z = box_muller(pcg.random(agents), pcg.random(agents))
            scores = 0.9 * scores + 0.1 * dual_roll_score(domain, fragments, z)

        th = DOMAIN_THRESHOLDS.get(domain, {"min_score": 60.0, "require_counter": False})
        confidence = float(np.mean(scores))
        has_counter = any(f.limitations for f in fragments)
        provenance_ok = all(f.provenance_ok() for f in fragments)
        
        # CRITICAL FIX: Track which fragments have provenance issues for transparency
        provenance_failures = []
        if not provenance_ok:
            for i, f in enumerate(fragments):
                if not f.provenance_ok():
                    source_id = getattr(f, 'source_id', 'unknown')
                    published_on = getattr(f, 'published_on', None)
                    reason = "missing_source_id" if source_id == "unknown" else "invalid_date_format"
                    provenance_failures.append({
                        "fragment_id": getattr(f, 'id', f'frag_{i}'),
                        "source_id": source_id,
                        "published_on": str(published_on),
                        "reason": reason
                    })

        if not fragments:
            abstention = "HALT_LOW_EVIDENCE"
        elif not provenance_ok:
            abstention = "HALT_PROVENANCE"
        elif th.get("require_counter") and not has_counter:
            abstention = "HALT_NO_COUNTERARG"
        elif confidence < th["min_score"]:
            abstention = "HALT_LOW_CONFIDENCE"
        elif not converged:
            abstention = "HALT_NON_CONVERGENCE"
        else:
            abstention = "ANSWER"

        replay = {
            "seed": seed,
            "agents": agents,
            "sub_questions": sub_questions,
            "score_mean": round(confidence, 4),
            "score_var": round(float(np.var(scores)), 6),
        }
        
        # CRITICAL FIX: Include provenance failures in output for transparency
        result = {"confidence": round(confidence, 2), "status": abstention, "replay": json.dumps(replay)}
        if provenance_failures:
            result["provenance_warnings"] = provenance_failures
        return result
