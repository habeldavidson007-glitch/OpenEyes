from __future__ import annotations

from dataclasses import asdict
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

from openeyes.knowledge.fragments import Fragment

WIKI_SEARCH = "https://en.wikipedia.org/w/rest.php/v1/search/title"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

HEADERS = {
    "User-Agent": "OpenEyes/1.0 (https://github.com/OpenEyes; contact@example.org)"
}


def _wiki_results(query: str, limit: int = 3) -> list[dict[str, Any]]:
    if requests is None:
        return []
    try:
        r = requests.get(WIKI_SEARCH, params={"q": query, "limit": limit}, timeout=8, headers=HEADERS)
        r.raise_for_status()
        return r.json().get("pages", [])
    except Exception:
        return []


def fetch_live_fragments(query: str, domain: str, limit: int = 3) -> list[Fragment]:
    pages = _wiki_results(query, limit=limit)
    out: list[Fragment] = []
    for p in pages:
        title = p.get("title")
        if not title:
            continue
        if requests is None:
            break
        try:
            s = requests.get(WIKI_SUMMARY.format(title=title.replace(" ", "_")), timeout=8, headers=HEADERS)
            s.raise_for_status()
            data = s.json()
            extract = data.get("extract", "")
            if not extract:
                continue
            out.append(
                Fragment(
                    claim=extract,
                    evidence=f"Wikipedia summary for {title}",
                    limitations=["General public source; verify with primary references for high-stakes use."],
                    sub_questions=[f"What is {title}?", f"How does {title} relate to {query}?"],
                    source_type="textbook" if domain == "medical" else "expert_blog",
                    source_id=f"wiki:{data.get('pageid', title)}",
                    source_url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    published_on="2024-01-01",
                    jurisdiction="global",
                    evidence_level="moderate",
                )
            )
        except Exception:
            continue
    return out
