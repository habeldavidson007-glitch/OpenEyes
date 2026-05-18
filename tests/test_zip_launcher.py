from __future__ import annotations

import run_openeyes


def test_dependency_mapping_present() -> None:
    assert "click" in run_openeyes.DEPENDENCIES
    assert run_openeyes.DEPENDENCIES["numpy"] == "numpy"


def test_no_install_flag_path(monkeypatch, tmp_path) -> None:
    def fake_import(name):
        raise ImportError(name)

    monkeypatch.setattr(run_openeyes.importlib, "import_module", fake_import)
    try:
        run_openeyes.ensure_local_deps(tmp_path, no_install=True)
        assert False
    except RuntimeError as exc:
        assert "Missing dependencies" in str(exc)
