from __future__ import annotations

from dataclasses import dataclass

from openeyes.core.engine import OpenEyesEngine


@dataclass
class QueryResult:
    payload: dict


class QueryService:
    def __init__(self, engine: OpenEyesEngine | None = None):
        self.engine = engine or OpenEyesEngine()

    def ask(self, query: str, domain: str | None = None) -> QueryResult:
        result = self.engine.answer(query=query, domain=domain)
        result.setdefault("routed_domain", result.get("domain", domain))
        if result.get("routing_confidence") is None:
            # proxy confidence until router exposes calibrated score
            conf = float(result.get("confidence", 0.0) or 0.0)
            result["routing_confidence"] = round(max(0.0, min(1.0, conf / 100.0)), 3)
        return QueryResult(payload=result)
