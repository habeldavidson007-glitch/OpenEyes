from __future__ import annotations


def decompose_query(query: str) -> list[str]:
    q = query.strip().rstrip("?")
    tokens = [t for t in q.split() if t]
    if len(tokens) < 6:
        return [q]
    chunks = [" ".join(tokens[: len(tokens)//2]), " ".join(tokens[len(tokens)//2 :])]
    return [c for c in chunks if c]
