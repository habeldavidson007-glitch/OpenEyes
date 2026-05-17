from __future__ import annotations

import run_openeyes


def test_required_dependency_list_present() -> None:
    assert "click" in run_openeyes.REQUIRED
    assert "rich" in run_openeyes.REQUIRED
    assert "numpy" in run_openeyes.REQUIRED
