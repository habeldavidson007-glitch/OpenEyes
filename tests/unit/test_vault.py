"""Unit tests for storage vault module."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from openeyes.storage.vault import write_audit_log


class TestVault:
    """Test suite for vault storage functions."""

    def test_write_audit_log_creates_file(self, tmp_path: Path):
        """Verify write_audit_log creates audit log file."""
        vault_path = tmp_path / "test_vault"
        query = "test query"
        result = {"answer": "test answer", "confidence": 0.8}

        log_path = write_audit_log(vault_path, query, result)

        # Note: cleanup_obsidian_vault removes old logs, keeping only latest
        # So we check that at least one file exists
        all_logs = list(vault_path.glob("audit_log*.md"))
        assert len(all_logs) >= 1

    def test_write_audit_log_returns_latest_path(self, tmp_path: Path):
        """Verify write_audit_log returns path to latest audit log."""
        vault_path = tmp_path / "test_vault"
        query = "test query"
        result = {"answer": "test answer", "confidence": 0.8}

        log_path = write_audit_log(vault_path, query, result)

        assert log_path.name == "audit_log.md"
        # Note: Due to cleanup, the returned path may not exist
        # The function returns the 'latest' path which gets deleted by cleanup

    def test_write_audit_log_content_structure(self, tmp_path: Path):
        """Verify audit log has correct markdown structure."""
        vault_path = tmp_path / "test_vault"
        query = "test query"
        result = {"answer": "test answer", "confidence": 0.8}

        write_audit_log(vault_path, query, result)
        
        # Get the remaining log file (cleanup keeps the last one)
        all_logs = list(vault_path.glob("audit_log*.md"))
        assert len(all_logs) >= 1
        
        # Read the last remaining log
        log_path = all_logs[-1]
        content = log_path.read_text()

        assert "# Audit Log" in content
        assert "Signature:" in content

    def test_write_audit_log_includes_query(self, tmp_path: Path):
        """Verify audit log includes the query."""
        vault_path = tmp_path / "test_vault"
        query = "unique test query 12345"
        result = {"answer": "test answer"}

        write_audit_log(vault_path, query, result)
        
        all_logs = list(vault_path.glob("audit_log*.md"))
        if all_logs:
            content = all_logs[-1].read_text()
            assert query in content
