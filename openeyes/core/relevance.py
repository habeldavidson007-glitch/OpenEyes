from __future__ import annotations

import re
from datetime import datetime


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{3,}", (text or "").lower()))


def score_fragment(query: str, routed_domain: str, fragment) -> float:
    q = _tokens(query)
    content = getattr(fragment, "content", "") or getattr(fragment, "claim", "") or getattr(fragment, "summary", "")
    f = _tokens(content)
    overlap = (len(q & f) / len(q)) if q else 0.0

    domain = (getattr(fragment, "domain", "") or "").lower()
    domain_bonus = 0.25 if domain == (routed_domain or "").lower() else 0.0

    cred = float(getattr(fragment, "success_rate_ema", 0.5) or 0.5)
    cred_score = max(0.0, min(1.0, cred)) * 0.2

    year = getattr(fragment, "year", None)
    recency = 0.0
    if isinstance(year, int):
        age = max(0, datetime.utcnow().year - year)
        recency = max(0.0, 1.0 - (age / 15.0)) * 0.15

    return overlap + domain_bonus + cred_score + recency


def rerank_fragments(query: str, routed_domain: str, fragments: list) -> list:
    return sorted(fragments, key=lambda f: score_fragment(query, routed_domain, f), reverse=True)
