#!/usr/bin/env python3
"""Minimal relevancy regression harness for OpenEyes."""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    return {t for t in re.findall(r"[a-zA-Z]{3,}", text.lower()) if t not in STOPWORDS}


def overlap_score(query: str, answer: str) -> float:
    q = tokenize(query)
    a = tokenize(answer)
    if not q:
        return 0.0
    return len(q & a) / len(q)


def evaluate() -> dict:
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
        results.append(
            {
                "query": case.query,
                "domain": case.domain,
                "answer": r.get("answer", ""),
                "confidence": r.get("confidence", 0),
                "overlap_score": round(score, 3),
            }
        )

    avg_score = sum(item["overlap_score"] for item in results) / len(results)
    return {"avg_overlap_score": round(avg_score, 3), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-overlap", type=float, default=None)
    args = parser.parse_args()

    payload = evaluate()
    print(json.dumps(payload, indent=2))

    if args.min_overlap is not None and payload["avg_overlap_score"] < args.min_overlap:
        print(
            f"[FAIL] avg_overlap_score={payload['avg_overlap_score']} is below threshold {args.min_overlap}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
