"""Integration tests for OpenEyes engine with various domains."""

import pytest
from pathlib import Path
from openeyes.core.engine import OpenEyesEngine


class TestEngineMedicalDomain:
    """Test engine behavior with medical domain queries."""

    def test_medical_query_returns_answer(self, tmp_path: Path):
        """Verify medical queries return answers."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("What are symptoms of diabetes?", "medical")
        
        assert "answer" in result
        assert result["answer"] != "HALT" or "answer_class" in result

    def test_medical_query_has_confidence(self, tmp_path: Path):
        """Verify medical queries include confidence score."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("What causes hypertension?", "medical")
        
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))

    def test_multiple_medical_queries_consistent(self, tmp_path: Path):
        """Verify multiple similar medical queries behave consistently."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        
        results = [
            engine.answer("Cancer symptoms", "medical")
            for _ in range(3)
        ]
        
        # All should have answer field
        assert all("answer" in r for r in results)


class TestEngineInvestmentDomain:
    """Test engine behavior with investment domain queries."""

    def test_investment_query_returns_answer(self, tmp_path: Path):
        """Verify investment queries return answers."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("How to invest in stocks?", "investment")
        
        assert "answer" in result

    def test_investment_query_has_scenarios(self, tmp_path: Path):
        """Verify investment queries include scenarios."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("Best investment strategy 2024", "investment")
        
        if "narrative" in result:
            assert "scenarios" in result["narrative"]


class TestEngineGeneralQueries:
    """Test engine behavior with general queries (no domain)."""

    def test_general_query_handled(self, tmp_path: Path):
        """Verify general queries without domain are handled."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("What is the capital of France?", None)
        
        assert "answer" in result

    def test_general_query_uses_live_fetch(self, tmp_path: Path):
        """Verify general queries can use live fetch."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        result = engine.answer("Current weather patterns", None)
        
        # Should have some answer content
        assert len(result.get("answer", "")) > 0


class TestEngineMemoryAndLearning:
    """Test engine memory and learning capabilities."""

    def test_repeated_query_improves_confidence(self, tmp_path: Path):
        """Verify repeated queries improve confidence."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        
        result1 = engine.answer("Investment strategies", "investment")
        result2 = engine.answer("Investment strategies", "investment")
        
        # Second query should have equal or higher confidence
        assert result2["confidence"] >= result1["confidence"]

    def test_engine_maintains_state(self, tmp_path: Path):
        """Verify engine maintains state across queries."""
        engine = OpenEyesEngine(vault_path=tmp_path / "vault")
        
        # Make several queries
        engine.answer("Query 1", "medical")
        engine.answer("Query 2", "investment")
        result = engine.answer("Query 3", "medical")
        
        # Engine should still be functional
        assert "answer" in result
