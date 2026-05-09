from __future__ import annotations

from pathlib import Path

from openeyes.core.engine import OpenEyesEngine
from openeyes.monte_carlo.engine import MonteCarloEngine


def test_pancreatic_cancer_5_runs(tmp_path: Path) -> None:
    vault = tmp_path / "obsidian_vault"
    engine = OpenEyesEngine(vault_path=vault)

    results = [engine.answer("Pancreatic Cancer Symptoms", "medical") for _ in range(5)]
    confidences = [r["confidence"] for r in results]
    print("confidences:", confidences)

    answer_count = sum(1 for r in results if r["status"] == "ANSWER")
    assert answer_count >= 4

    audit_files = list(vault.glob("audit_log*.md"))
    assert len(audit_files) == 1
    assert (vault / "audit_log.md").exists()


def test_stable_seed_deterministic() -> None:
    s1 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
    s2 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
    assert s1 == s2
