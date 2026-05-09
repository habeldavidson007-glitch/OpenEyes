from __future__ import annotations


def compose_narrative(query: str, domain: str, status: str, confidence: float, sub_questions: list[str]) -> dict:
    risk = "high" if confidence < 50 else "moderate" if confidence < 75 else "lower"
    scenarios = {
        "best": (
            f"If you pursue {domain} through regulated, diversified, and long-horizon decisions, "
            "you can build compounding outcomes while controlling downside volatility."
        ),
        "likely": (
            "Most real-world outcomes are uneven: progress is gradual, and performance depends on consistency, "
            "risk discipline, and avoiding emotionally-driven decisions."
        ),
        "worst": (
            f"Shortcut-oriented behavior in {domain} (high leverage, hype-chasing, concentration risk) "
            "can rapidly destroy capital and create long recovery windows."
        ),
    }
    philosophy = (
        "OpenEyes prioritizes capital-preservation and evidence-backed decisions over 'get-rich-fast' narratives. "
        "Speed without risk controls usually trades short-term excitement for long-term fragility."
    )
    logic_assembly = [
        "Routed query to domain using semantic keywords and intent cues.",
        "Evaluated confidence using deterministic Monte Carlo replay path.",
        "Applied safety policy: low evidence triggers conservative recommendation framing.",
    ]
    recommendation = (
        "Build a staged plan: emergency reserve, diversified core allocation, capped speculation budget, "
        "and periodic review against documented risk limits."
    )
    return {
        "context": f"Interpreted query in domain '{domain}' with status {status}.",
        "risk_level": risk,
        "sub_questions": sub_questions,
        "scenarios": scenarios,
        "logic_assembly": logic_assembly,
        "philosophy": philosophy,
        "recommendation": recommendation,
    }
