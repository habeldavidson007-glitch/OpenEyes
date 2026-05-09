from __future__ import annotations


def compose_narrative(query: str, domain: str, status: str, confidence: float, sub_questions: list[str]) -> dict:
    risk = "high" if confidence < 50 else "moderate" if confidence < 75 else "lower"
    scenarios = {
        "best": f"Disciplined, evidence-backed {domain} strategy with controlled risk.",
        "likely": f"Mixed outcomes; progress depends on consistency and verified guidance.",
        "worst": f"High-risk shortcuts may lead to severe downside in {domain}.",
    }
    recommendation = (
        "Use verified primary sources, define risk limits, and seek licensed experts for real-world decisions."
    )
    return {
        "context": f"Interpreted query in domain '{domain}' with status {status}.",
        "risk_level": risk,
        "sub_questions": sub_questions,
        "scenarios": scenarios,
        "recommendation": recommendation,
    }
