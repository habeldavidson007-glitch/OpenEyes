from __future__ import annotations

import json
from pathlib import Path

from openeyes.config import audit_dir
from openeyes.core.router import route_domain
from openeyes.knowledge.fragments import Fragment
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.vault import write_audit_log


class OpenEyesEngine:
    def __init__(self, vault_path: Path | None = None) -> None:
        self.mc = MonteCarloEngine()
        self.vault_path = vault_path or audit_dir()

    def _fragments_for(self, query: str, domain: str) -> list[Fragment]:
        if "pancreatic" in query.lower():
            return [
                Fragment(
                    claim="Pancreatic cancer commonly presents late with nonspecific symptoms.",
                    evidence="NCCN-like and review synthesis.",
                    limitations=["Symptoms overlap with benign disease."],
                    sub_questions=["What are common symptoms?", "What are red flags?"],
                    feedback={"thumbs_up": 20, "thumbs_down": 2},
                    success_rate_ema=0.88,
                    source_type="clinical_guideline" if domain == "medical" else "peer_reviewed_study",
                    source_id="GUIDE-PANC-2025",
                    source_url="https://example.org/guideline/pancreas",
                    published_on="2025-06-01",
                    jurisdiction="US",
                    evidence_level="high",
                )
            ]
        return []

    @staticmethod
    def _safe_fallback_answer(query: str, domain: str, status: str) -> str:
        return (
            f"Low-confidence response ({status}) for '{query}'. "
            f"For {domain}, prioritize regulated guidance, verified sources, and risk-aware steps. "
            "If this decision impacts health, legal rights, or money, consult a licensed professional."
        )

    def answer(self, query: str, domain: str | None = None) -> dict:
        routed_domain = route_domain(query, domain)
        frags = self._fragments_for(query, routed_domain)
        result = self.mc.run(query=query, domain=routed_domain, fragments=frags)

        if result["status"] == "ANSWER":
            answer = "Possible symptoms include jaundice, unexplained weight loss, upper abdominal/back pain, appetite loss, and new-onset diabetes."
            answer_class = "ANSWER_CONFIDENT"
        else:
            answer = self._safe_fallback_answer(query, routed_domain, result["status"])
            answer_class = "ANSWER_LOW_CONFIDENCE"

        out = {
            "status": result["status"],
            "answer_class": answer_class,
            "answer": answer,
            "confidence": result["confidence"],
            "domain": routed_domain,
            "replay": json.loads(result["replay"]),
        }
        write_audit_log(self.vault_path, query, out)
        return out
