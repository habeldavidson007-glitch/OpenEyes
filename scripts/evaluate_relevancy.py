#!/usr/bin/env python3
"""Minimal relevancy regression harness for OpenEyes.

Runs a fixed query set and computes lexical overlap between query terms and answer terms.
This is not a semantic metric, but it quickly catches severe off-topic regressions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openeyes.core.engine import OpenEyesEngine


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with", "is", "are", "what", "how", "does",
}


@dataclass
class EvalCase:
    query: str
    domain: str | None = None


def tokenize(text: str) -> set[str]:
    terms = {t for t in re.findall(r"[a-zA-Z]{3,}", text.lower()) if t not in STOPWORDS}
    return terms


def overlap_score(query: str, answer: str) -> float:
    q = tokenize(query)
    a = tokenize(answer)
    if not q:
        return 0.0
    return len(q & a) / len(q)


def main() -> None:
    cases = [
        EvalCase("What are the ethical guidelines for autonomous vehicles?", "governance"),
        EvalCase("Calculate projected ROI of a 60/40 portfolio", "investment"),
        EvalCase("Detail GDPR compliance for biometric data", "governance"),
        EvalCase("What is first-line treatment for type 2 diabetes?", "healthcare"),
        EvalCase("How does quantitative easing affect inflation?", "economy"),
    ]

    engine = OpenEyesEngine()
    results = []
    for case in cases:
        r = engine.answer(case.query, case.domain)
        score = overlap_score(case.query, r.get("answer", ""))
        results.append({
            "query": case.query,
            "domain": case.domain,
            "answer": r.get("answer", ""),
            "confidence": r.get("confidence", 0),
            "overlap_score": round(score, 3),
        })

    avg_score = sum(item["overlap_score"] for item in results) / len(results)
    payload = {"avg_overlap_score": round(avg_score, 3), "results": results}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
