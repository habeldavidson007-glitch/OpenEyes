from __future__ import annotations

from pathlib import Path
from typing import Any

from openeyes.storage.binary_lib import load_binary, save_binary


def ingest_case(path: Path, case: dict[str, Any], max_items: int = 1000) -> None:
    data: list[dict[str, Any]]
    if path.exists():
        data = load_binary(path)
    else:
        data = []
    data.append(case)
    if len(data) > max_items:
        data = data[-max_items:]
    save_binary(path, data)


def retrieve_similar(path: Path, query: str, domain: str, top_k: int = 3) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = load_binary(path)
    q = set(query.lower().split())
    scored = []
    for item in data:
        if item.get("domain") != domain:
            continue
        w = set(str(item.get("query", "")).lower().split())
        score = len(q & w)
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:top_k] if score > 0]
