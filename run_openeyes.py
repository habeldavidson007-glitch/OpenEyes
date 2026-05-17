#!/usr/bin/env python3
"""Zero-setup launcher for OpenEyes from a downloaded ZIP.

Usage:
  python run_openeyes.py --help
  python run_openeyes.py ask "What is inflation?" --domain economy

This script installs missing runtime dependencies into a local folder
(`.openeyes/vendor`) and then runs the OpenEyes CLI.
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

REQUIRED = ["click", "rich", "numpy", "scipy", "requests"]


def ensure_local_deps(repo_root: Path) -> None:
    vendor = repo_root / ".openeyes" / "vendor"
    vendor.mkdir(parents=True, exist_ok=True)

    missing: list[str] = []
    for pkg in REQUIRED:
        try:
            importlib.import_module(pkg)
        except Exception:
            missing.append(pkg)

    if missing:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--target",
            str(vendor),
            *missing,
        ]
        subprocess.check_call(cmd)

    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    ensure_local_deps(repo_root)

    os.environ.setdefault("PYTHONPATH", str(repo_root))
    from openeyes.cli import cli

    # Delegate all CLI args to click app.
    return int(cli.main(args=sys.argv[1:], prog_name="openeyes", standalone_mode=False) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
