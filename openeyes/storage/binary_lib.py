from __future__ import annotations

import gzip
import pickle
from pathlib import Path
from typing import Any


def save_binary(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_binary(path: Path) -> Any:
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


def cleanup_obsidian_vault(vault_path: Path) -> None:
    vault_path.mkdir(parents=True, exist_ok=True)
    logs = sorted(vault_path.glob("audit_log*.md"), key=lambda p: p.stat().st_mtime)
    for old in logs[:-1]:
        old.unlink(missing_ok=True)
