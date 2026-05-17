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
        return QueryResult(payload=result)
