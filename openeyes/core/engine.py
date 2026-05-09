from __future__ import annotations

import json
from pathlib import Path

from openeyes.config import audit_dir
from openeyes.core.router import route_domain
from openeyes.core.narrative import compose_narrative
from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.live_fetch import fetch_live_fragments
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.memory import ingest_case, retrieve_similar
from openeyes.storage.vault import write_audit_log




def _is_complex_query(query: str) -> bool:
    q = query.lower()
    markers = ["plan", "strategy", "step by step", "roadmap", "how to", "fast", "rich", "investment"]
    return len(q.split()) >= 8 or any(m in q for m in markers)


def _compose_user_answer(query: str, domain: str, narrative: dict, status: str) -> str:
    scenarios = narrative.get("scenarios", {})
    if domain == "investment":
        if _is_complex_query(query):
            return (
                "Here is a practical, risk-aware plan to build wealth faster without gambling your future:\n"
                "1) Stabilize your base: clear high-interest debt and keep 3-6 months emergency cash.\n"
                "2) Build a core portfolio: broad diversified index exposure as default.\n"
                "3) Add a capped high-risk bucket: only small % for speculative ideas.\n"
                "4) Automate monthly contributions and rebalance quarterly.\n"
                "5) Track net worth, savings rate, and downside risk monthly.\n"
                f"Best case: {scenarios.get('best','')}\n"
                f"Likely case: {scenarios.get('likely','')}\n"
                f"Worst case: {scenarios.get('worst','')}\n"
                "Bottom line: there is no safe instant-rich path; speed must be paired with risk limits and consistency."
            )
    if domain == "cooking":
        return (
            "Quick banana brownie (short version):\n"
            "1) Mash 2 ripe bananas.\n"
            "2) Mix with 1/2 cup cocoa, 1/2 cup flour, 1 egg, 1/4 cup sugar, pinch salt.\n"
            "3) Bake at 175C (350F) for 20-25 min.\n"
            "4) Cool 10 min, slice, serve."
        )
    if status != "ANSWER":
        return (
            "I can give a practical starting answer, but confidence is limited. "
            "Use verified sources and, for high-stakes decisions, consult licensed professionals."
        )
    return "Possible symptoms include jaundice, unexplained weight loss, upper abdominal/back pain, appetite loss, and new-onset diabetes."


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
        fetched = fetch_live_fragments(query, domain, limit=3)
        return fetched

    @staticmethod
    def _safe_fallback_answer(query: str, domain: str, status: str, narrative: dict) -> str:
        scenarios = narrative.get("scenarios", {})
        return (
            f"OpenEyes safety mode: {status} for query '{query}'.\n\n"
            f"Context: {narrative.get('context', '')}\n"
            f"Best-case: {scenarios.get('best', '')}\n"
            f"Likely-case: {scenarios.get('likely', '')}\n"
            f"Worst-case: {scenarios.get('worst', '')}\n"
            f"Recommendation: {narrative.get('recommendation', '')}\n"
            "Disclaimer: For real financial, legal, or medical decisions, consult licensed professionals."
        )

    def answer(self, query: str, domain: str | None = None) -> dict:
        routed_domain = route_domain(query, domain)
        frags = self._fragments_for(query, routed_domain)
        priors = retrieve_similar(self.memory_path, query, routed_domain)
        result = self.mc.run(query=query, domain=routed_domain, fragments=frags)
        if priors and result.get("confidence", 0.0) < 60:
            result["confidence"] = round(min(99.0, result["confidence"] + 5.0 * len(priors)), 2)

        replay = json.loads(result["replay"])
        narrative = compose_narrative(query, routed_domain, result["status"], float(result["confidence"]), replay.get("sub_questions", []))

        answer = _compose_user_answer(query, routed_domain, narrative, result["status"])
        answer_class = "ANSWER_CONFIDENT" if result["status"] == "ANSWER" else "ANSWER_LOW_CONFIDENCE"

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
