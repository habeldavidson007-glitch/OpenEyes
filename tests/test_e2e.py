from __future__ import annotations

from pathlib import Path

from openeyes.core.engine import OpenEyesEngine
from openeyes.monte_carlo.engine import MonteCarloEngine


def test_pancreatic_cancer_5_runs(tmp_path: Path) -> None:
    vault = tmp_path / "obsidian_vault"
    engine = OpenEyesEngine(vault_path=vault, mode="assistive")

    results = [engine.answer("Pancreatic Cancer Symptoms", "medical") for _ in range(5)]
    answer_count = sum(1 for r in results if r["answer_class"].startswith("ANSWER"))
    assert answer_count >= 4


def test_assistive_mode_always_answers(tmp_path: Path) -> None:
    engine = OpenEyesEngine(vault_path=tmp_path / "v", mode="assistive")
    r = engine.answer("Fastest way to get rich using investment?", "investment")
    assert r["answer"] != "HALT"
    assert r["answer_class"] == "ANSWER_LOW_CONFIDENCE"


def test_stable_seed_deterministic() -> None:
    s1 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
    s2 = MonteCarloEngine.stable_seed("Pancreatic Cancer Symptoms", "medical")
    assert s1 == s2
