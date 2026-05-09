from __future__ import annotations

import json
from pathlib import Path

from openeyes.knowledge.fragments import Fragment
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.vault import write_audit_log


class OpenEyesEngine:
    def __init__(self, vault_path: Path | None = None) -> None:
        self.mc = MonteCarloEngine()
        self.vault_path = vault_path or Path("obsidian_vault")

    def _fragments_for(self, query: str, domain: str) -> list[Fragment]:
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
        ] if "pancreatic" in query.lower() else []

    def answer(self, query: str, domain: str) -> dict:
        frags = self._fragments_for(query, domain)
        result = self.mc.run(query=query, domain=domain, fragments=frags)

        if result["status"] == "ANSWER":
            answer = "Possible symptoms include jaundice, unexplained weight loss, upper abdominal/back pain, appetite loss, and new-onset diabetes."
        else:
            answer = "HALT"

        out = {
            "status": result["status"],
            "answer": answer,
            "confidence": result["confidence"],
            "domain": domain,
            "replay": json.loads(result["replay"]),
        }
        write_audit_log(self.vault_path, query, out)
        return out
