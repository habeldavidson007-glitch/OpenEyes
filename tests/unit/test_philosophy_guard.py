"""Unit tests for Philosophy Guard."""

import pytest
from shared_core.philosophy_guard import PhilosophyGuard


class TestPhilosophyGuard:
    """Test suite for PhilosophyGuard class."""

    def test_initialization(self):
        """Verify PhilosophyGuard can be initialized."""
        guard = PhilosophyGuard()
        assert guard is not None
        assert hasattr(guard, 'rules')
        assert hasattr(guard, 'validate_proposal')

    def test_validate_proposal_basic(self):
        """Verify validate_proposal method exists and accepts basic input."""
        guard = PhilosophyGuard()
        proposal = {
            "id": "test-001",
            "type": "medical",
            "content": "Cancer is a disease.",
            "tags": ["health", "medical"]
        }
        # Should not raise exception
        result = guard.validate_proposal(proposal)
        assert result is not None
        assert "passed" in result
        assert "rule_results" in result

    def test_validate_proposal_returns_structure(self):
        """Verify validate_proposal returns expected structure."""
        guard = PhilosophyGuard()
        proposal = {
            "id": "test-002",
            "domain": "investment",
            "content": "Investment advice"
        }
        result = guard.validate_proposal(proposal)
        
        assert "proposal_id" in result
        assert "proposal_type" in result
        assert "domain" in result
        assert "passed" in result
        assert "rule_results" in result
        assert "rejected_by" in result
        assert "warnings" in result

    def test_validate_proposal_empty(self):
        """Verify validation handles empty proposal."""
        guard = PhilosophyGuard()
        proposal = {}
        # Should handle gracefully
        result = guard.validate_proposal(proposal)
        assert result is not None
        assert "passed" in result
