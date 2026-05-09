from __future__ import annotations

from dataclasses import dataclass
from typing import List

from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.live_fetch import fetch_live_fragments, jit_synthesize_fragments


@dataclass
class RetrievalRecord:
    claim: str
    source: str
    url: str
    published_on: str
    confidence: float
    fragment: Fragment


def retrieve_records(query: str, domain: str, limit: int) -> List[RetrievalRecord]:
    frags = fetch_live_fragments(query, domain, limit=limit)
    if not frags:
        frags = jit_synthesize_fragments(query, domain, limit=limit)
    records: List[RetrievalRecord] = []
    for f in frags:
        confidence = 0.9 if getattr(f, "evidence_level", "moderate") == "high" else 0.7
        records.append(
            RetrievalRecord(
                claim=f.claim,
                source=f.evidence,
                url=getattr(f, "source_url", ""),
                published_on=getattr(f, "published_on", ""),
                confidence=confidence,
                fragment=f,
            )
        )
    return records
