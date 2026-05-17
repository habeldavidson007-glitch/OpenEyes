from __future__ import annotations

import json

from click.testing import CliRunner

from openeyes.cli import cli


def test_help_lists_new_contract_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ask" in result.output
    assert "doctor" in result.output
    assert "config" in result.output
    assert "version" in result.output


def test_doctor_json_schema() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "doctor"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["error"] is None
    data = payload["data"]
    for key in ["python", "vault_root_exists", "audit_dir_exists", "audit_file_count"]:
        assert key in data
    assert payload["cli_schema_version"] == "1"


def test_config_json_schema() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "config"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert "vault_root" in payload["data"]
    assert "audit_dir" in payload["data"]


def test_version_modes() -> None:
    runner = CliRunner()
    human = runner.invoke(cli, ["version"])
    assert human.exit_code == 0
    assert "OpenEyes 0.1.0" in human.output

    machine = runner.invoke(cli, ["--json", "version"])
    assert machine.exit_code == 0
    payload = json.loads(machine.output)
    assert payload["data"]["version"] == "0.1.0"


def test_legacy_query_is_hidden_from_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "query" not in result.output


def test_json_schema_version_in_version_command() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "version"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["cli_schema_version"] == "1"
    assert payload["ok"] is True


def test_ask_help_mentions_auto_routing() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["ask", "--help"])
    assert result.exit_code == 0
    assert "auto-routes domain by default" in result.output
