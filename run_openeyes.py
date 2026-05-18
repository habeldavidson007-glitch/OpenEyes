#!/usr/bin/env python3
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

DEPENDENCIES = {
    "click": "click",
    "rich": "rich",
    "numpy": "numpy",
    "scipy": "scipy",
    "requests": "requests",
}


def ensure_local_deps(repo_root: Path, no_install: bool = False) -> None:
    vendor = repo_root / ".openeyes" / "vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))

    missing = []
    for module_name, package_name in DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(package_name)

    if missing and no_install:
        raise RuntimeError(f"Missing dependencies: {', '.join(missing)}. Re-run without --no-install.")

    if missing:
        cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--target", str(vendor), *missing]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Automatic dependency installation failed. Check internet/proxy settings, or install manually with: "
                f"{sys.executable} -m pip install --target {vendor} {' '.join(missing)}"
            ) from exc


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    args = sys.argv[1:]
    no_install = False
    if "--no-install" in args:
        args.remove("--no-install")
        no_install = True

    try:
        ensure_local_deps(repo_root, no_install=no_install)
    except RuntimeError as exc:
        print(f"[OpenEyes launcher] {exc}", file=sys.stderr)
        return 2

    from openeyes.cli import cli

    return int(cli.main(args=args, prog_name="openeyes", standalone_mode=False) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
