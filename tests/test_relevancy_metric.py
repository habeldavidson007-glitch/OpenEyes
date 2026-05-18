from scripts.evaluate_relevancy import overlap_score


def test_overlap_score_higher_for_relevant_answer() -> None:
    q = "ethical guidelines for autonomous vehicles"
    relevant = "Ethical guidelines for autonomous vehicles include safety transparency and accountability."
    irrelevant = "Portfolio diversification and ESG funds can reduce risk in investing."

    assert overlap_score(q, relevant) > overlap_score(q, irrelevant)


def test_quality_eval_payload_shape() -> None:
    from scripts.evaluate_answer_quality import evaluate
    out = evaluate()
    assert "avg_domain_accuracy" in out
    assert "avg_concept_score" in out
    assert isinstance(out["results"], list)


def test_inflation_query_mentions_inflation_or_prices() -> None:
    from openeyes.services.query_service import QueryService
    out = QueryService().ask("What is inflation?").payload
    ans = (out.get("answer") or "").lower()
    assert ("inflation" in ans) or ("price" in ans)


def test_routing_confidence_non_null() -> None:
    from openeyes.services.query_service import QueryService
    out = QueryService().ask("What is inflation?").payload
    assert out.get("routing_confidence") is not None
    assert 0.0 <= float(out["routing_confidence"]) <= 1.0


def test_groundedness_fields_present() -> None:
    from openeyes.services.query_service import QueryService
    out = QueryService().ask("What is inflation?").payload
    assert "grounded_claims" in out
    assert "ungrounded_claims_count" in out
    assert "groundedness_score" in out
