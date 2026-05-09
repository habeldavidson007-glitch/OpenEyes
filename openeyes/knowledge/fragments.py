from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Fragment:
    claim: str
    evidence: str
    limitations: list[str]
    sub_questions: list[str]
    source_type: str = "peer_reviewed_study"
    source_id: str = "unknown"
    source_url: str = ""
    published_on: str = ""
    jurisdiction: str = "global"
    evidence_level: str = "moderate"
    feedback: dict[str, int] = field(default_factory=lambda: {"thumbs_up": 0, "thumbs_down": 0})
    success_rate_ema: float = 0.7

    @property
    def effective_weight(self) -> float:
        up = self.feedback.get("thumbs_up", 0)
        down = self.feedback.get("thumbs_down", 0)
        total = max(up + down, 1)
        feedback_ratio = up / total
        return 0.75 * self.success_rate_ema + 0.25 * feedback_ratio

    def provenance_ok(self) -> bool:
        if not self.source_id or self.source_id == "unknown":
            return False
        if not self.published_on:
            return False
        try:
            date.fromisoformat(self.published_on)
        except ValueError:
            return False
        return True


def migrate_fragment(payload: dict) -> Fragment:
    claim = payload.get("claim") or payload.get("content") or ""
    return Fragment(
        claim=claim,
        evidence=payload.get("evidence", ""),
        limitations=payload.get("limitations", []),
        sub_questions=payload.get("sub_questions", []),
        feedback=payload.get("feedback", {"thumbs_up": 0, "thumbs_down": 0}),
        success_rate_ema=float(payload.get("success_rate_ema", 0.7)),
        source_type=payload.get("source_type", "peer_reviewed_study"),
        source_id=payload.get("source_id", "unknown"),
        source_url=payload.get("source_url", ""),
        published_on=payload.get("published_on", ""),
        jurisdiction=payload.get("jurisdiction", "global"),
        evidence_level=payload.get("evidence_level", "moderate"),
    )
