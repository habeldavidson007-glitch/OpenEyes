from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fragment:
    claim: str
    evidence: str
    limitations: list[str]
    sub_questions: list[str]
    feedback: dict[str, int] = field(default_factory=lambda: {"thumbs_up": 0, "thumbs_down": 0})
    success_rate_ema: float = 0.7
    source_type: str = "peer_reviewed_study"

    @property
    def effective_weight(self) -> float:
        up = self.feedback.get("thumbs_up", 0)
        down = self.feedback.get("thumbs_down", 0)
        total = max(up + down, 1)
        feedback_ratio = up / total
        return 0.75 * self.success_rate_ema + 0.25 * feedback_ratio


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
    )
