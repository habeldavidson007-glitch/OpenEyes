from __future__ import annotations

CREDIBILITY_HIERARCHIES: dict[str, dict[str, int]] = {
    "economy": {
        "peer_reviewed_study": 95,
        "government_source": 90,
        "clinical_guideline": 88,
        "news_article": 65,
        "textbook": 80,
        "forum": 20
    },
    "healthcare": {
        "clinical_guideline": 98,
        "peer_reviewed_study": 95,
        "textbook": 85,
        "news_article": 55,
        "forum": 20
    },
    # keep existing entries below
    "medical": {"clinical_guideline": 98, "peer_reviewed_study": 95, "textbook": 85, "forum": 25},
    "engineering": {"iso_standard": 98, "code": 95, "handbook": 80},
    "cooking": {"culinary_institution": 95, "expert_blog": 75, "forum": 35},
    "trading": {"sec_filing": 98, "regulatory_guidance": 95, "analyst_report": 70},
    "investment": {"sec_filing": 98, "regulatory_guidance": 95, "analyst_report": 70},
    "legal": {"statute": 98, "case_law": 94, "secondary_source": 75},
}


def get_credibility_score(domain: str, source_type: str) -> int:
    return CREDIBILITY_HIERARCHIES.get(domain, {}).get(source_type, 50)
