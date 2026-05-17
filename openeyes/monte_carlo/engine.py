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

    def run(self, query: str, domain: str, fragments) -> dict:
        sub_questions = decompose_query(query)
        agents = 1024  # power-of-two for Sobol balance
        seed = self.stable_seed(query, domain)
        pcg = PCG64(seed=seed)
        sobol = sobol_vectors(agents, dim=2)
        noise = box_muller(pcg.random(agents), sobol[:, 1])
        
        # Extract Fragment objects from RetrievalRecord if needed
        fragment_objects = []
        for f in fragments:
            if hasattr(f, 'fragment'):
                # It's a RetrievalRecord, extract the Fragment
                fragment_objects.append(f.fragment)
            else:
                # It's already a Fragment
                fragment_objects.append(f)
        
        scores = dual_roll_score(domain, fragment_objects, noise)

        converged = False
        for _ in range(16):
            if variation(scores) < 0.05:
                converged = True
                break
            z = box_muller(pcg.random(agents), pcg.random(agents))
            scores = 0.9 * scores + 0.1 * dual_roll_score(domain, fragment_objects, z)

        th = DOMAIN_THRESHOLDS.get(domain, {"min_score": 60.0, "require_counter": False})
        confidence = float(np.mean(scores))
        has_counter = any(getattr(f, 'limitations', []) for f in fragment_objects)
        provenance_ok = all(getattr(f, 'provenance_ok', lambda: True)() if callable(getattr(f, 'provenance_ok', None)) else getattr(f, 'provenance_ok', True) for f in fragment_objects)

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
        return {"confidence": round(confidence, 2), "status": abstention, "replay": json.dumps(replay)}
    
    def evaluate(self, query: str, domain: str, fragments: list[Fragment]) -> dict:
        """Alias for run() method for API compatibility."""
        result = self.run(query, domain, fragments)
        # Add additional fields expected by the engine
        result['narrative'] = {
            'scenarios': [],
            'confidence': result.get('confidence', 0.0)
        }
        result['data_recency_years'] = 2
        result['answer_class'] = 'ANSWER_HIGH_CONFIDENCE' if result.get('confidence', 0) >= 0.7 else 'ANSWER_LOW_CONFIDENCE'
        return result
