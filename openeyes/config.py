from __future__ import annotations

import os
from pathlib import Path


def vault_root() -> Path:
    return Path(os.getenv("OPENEYES_VAULT_ROOT", ".openeyes/vault"))


def audit_dir() -> Path:
    return vault_root() / "audit"


def reports_dir() -> Path:
    return vault_root() / "reports"


def failures_dir() -> Path:
    return vault_root() / "failures"
