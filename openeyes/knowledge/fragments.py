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
    # Domain metadata for proper filtering
    domain: str = "unknown"
    sector: str = "unknown"
    topic: str = ""
    reasoning_role: str = "definition"
    tags: list[str] = field(default_factory=list)
    content: str = ""
    year: int = 0
    source: str = ""
    credibility_class: str = "peer_reviewed_study"

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
    # Handle new domain-based fragment format
    if 'domain' in payload and 'sector' in payload:
        # New format: domain, sector, reasoning_role, content
        claim = payload.get("content", "")
        role = payload.get("reasoning_role", "definition")
        domain = payload.get("domain", "")
        sector = payload.get("sector", "")
        
        # Build evidence from content and metadata
        evidence_parts = []
        if claim:
            evidence_parts.append(claim)
        if payload.get('source_url'):
            evidence_parts.append(f"Source: {payload['source_url']}")
        if payload.get('year'):
            evidence_parts.append(f"Year: {payload['year']}")
        evidence = "\n".join(evidence_parts)
        
        return Fragment(
            claim=claim,
            evidence=evidence,
            limitations=[],
            sub_questions=[],
            feedback=payload.get("feedback", {"thumbs_up": 0, "thumbs_down": 0}),
            success_rate_ema=float(payload.get("credibility_score", 0.7)),
            source_type=payload.get("credibility_class", "peer_reviewed_study"),
            source_id=payload.get("id", "unknown"),
            source_url=payload.get("source_url", ""),
            published_on=str(payload.get("year", "")),
            jurisdiction=payload.get("jurisdiction", "global"),
            evidence_level=payload.get("evidence_level", "moderate"),
            # Domain metadata
            domain=domain,
            sector=sector,
            topic=payload.get("topic", ""),
            reasoning_role=role,
            tags=payload.get("tags", []),
            content=claim,
            year=int(payload.get("year", 0)) if payload.get("year") else 0,
            source=payload.get("source", ""),
            credibility_class=payload.get("credibility_class", "peer_reviewed_study"),
        )
    
    # Legacy format handling
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
