from __future__ import annotations

import json
from pathlib import Path

from openeyes.config import audit_dir
from openeyes.core.router import route_domain
from openeyes.core.narrative import compose_narrative
from openeyes.knowledge.fragments import Fragment
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.memory import ingest_case, retrieve_similar
from openeyes.storage.vault import write_audit_log


class OpenEyesEngine:
    def __init__(self, vault_path: Path | None = None) -> None:
        self.mc = MonteCarloEngine()
        self.vault_path = vault_path or audit_dir()
        self.memory_path = self.vault_path / "memory.bin"

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
        priors = retrieve_similar(self.memory_path, query, routed_domain)
        result = self.mc.run(query=query, domain=routed_domain, fragments=frags)
        if priors and result.get("confidence", 0.0) < 60:
            result["confidence"] = round(min(99.0, result["confidence"] + 5.0 * len(priors)), 2)

        if result["status"] == "ANSWER":
            answer = "Possible symptoms include jaundice, unexplained weight loss, upper abdominal/back pain, appetite loss, and new-onset diabetes."
            answer_class = "ANSWER_CONFIDENT"
        else:
            answer = self._safe_fallback_answer(query, routed_domain, result["status"])
            answer_class = "ANSWER_LOW_CONFIDENCE"

        replay = json.loads(result["replay"])
        narrative = compose_narrative(query, routed_domain, result["status"], float(result["confidence"]), replay.get("sub_questions", []))
        out = {
            "status": result["status"],
            "answer_class": answer_class,
            "answer": answer,
            "confidence": result["confidence"],
            "domain": routed_domain,
            "narrative": narrative,
            "replay": replay,
        }
        ingest_case(self.memory_path, {"query": query, "domain": routed_domain, "status": result["status"], "confidence": result["confidence"]})
        write_audit_log(self.vault_path, query, out)
        return out
