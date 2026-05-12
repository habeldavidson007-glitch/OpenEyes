"""Unit tests for Monte Carlo engine."""

import pytest
from openeyes.monte_carlo.engine import MonteCarloEngine


class TestMonteCarloEngine:
    """Test suite for MonteCarloEngine class."""

    def test_stable_seed_deterministic(self):
        """Verify stable_seed produces same result for same input."""
        s1 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
        s2 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
        assert s1 == s2

    def test_stable_seed_different_inputs(self):
        """Verify stable_seed produces different results for different inputs."""
        s1 = MonteCarloEngine.stable_seed("query1", "domain1")
        s2 = MonteCarloEngine.stable_seed("query2", "domain2")
        assert s1 != s2

    def test_stable_seed_consistent_across_calls(self):
        """Verify stable_seed is consistent across multiple calls."""
        query = "test query"
        domain = "test_domain"
        seeds = [MonteCarloEngine.stable_seed(query, domain) for _ in range(10)]
        assert len(set(seeds)) == 1  # All seeds should be identical

    def test_initialization(self):
        """Verify MonteCarloEngine can be initialized."""
        engine = MonteCarloEngine()
        assert engine is not None
        assert hasattr(engine, 'stable_seed')
