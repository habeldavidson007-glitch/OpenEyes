#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openeyes.services.query_service import QueryService


@dataclass
class GoldCase:
    query: str
    expected_domain: str
    must_include: list[str]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{4,}", text.lower()))


def concept_score(answer: str, concepts: list[str]) -> float:
    a = _tokens(answer)
    if not concepts:
        return 1.0
    hits = sum(1 for c in concepts if c.lower() in a)
    return hits / len(concepts)


def evaluate() -> dict:
    cases = [
        GoldCase("How does inflation affect bond prices?", "economy", ["inflation", "bond", "rates"]),
        GoldCase("What are symptoms of type 2 diabetes?", "healthcare", ["diabetes", "symptoms", "glucose"]),
        GoldCase("How does a bill become law in the US?", "governance", ["congress", "bill", "law"]),
        GoldCase("Explain quantum entanglement basics", "sat", ["quantum", "entanglement"]),
    ]
    svc = QueryService()
    results = []
    for c in cases:
        r = svc.ask(c.query).payload
        ans = (r.get("answer") or "").lower()
        routed = (r.get("domain") or "").lower()
        domain_ok = 1.0 if routed == c.expected_domain else 0.0
        cscore = concept_score(ans, c.must_include)
        results.append({"query": c.query, "routed_domain": routed, "expected_domain": c.expected_domain, "domain_ok": domain_ok, "concept_score": round(cscore, 3)})

    avg_domain = sum(x["domain_ok"] for x in results) / len(results)
    avg_concept = sum(x["concept_score"] for x in results) / len(results)
    return {"avg_domain_accuracy": round(avg_domain, 3), "avg_concept_score": round(avg_concept, 3), "results": results}


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
