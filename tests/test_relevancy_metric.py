from scripts.evaluate_relevancy import overlap_score


def test_overlap_score_higher_for_relevant_answer() -> None:
    q = "ethical guidelines for autonomous vehicles"
    relevant = "Ethical guidelines for autonomous vehicles include safety transparency and accountability."
    irrelevant = "Portfolio diversification and ESG funds can reduce risk in investing."

    assert overlap_score(q, relevant) > overlap_score(q, irrelevant)
