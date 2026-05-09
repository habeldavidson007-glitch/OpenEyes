from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openeyes.storage.binary_lib import cleanup_obsidian_vault


def write_audit_log(vault_path: Path, query: str, result: dict) -> Path:
    vault_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    p = vault_path / f"audit_log_{ts}.md"
    p.write_text(f"# Audit Log\n\nQuery: {query}\n\nResult: {result}\n", encoding="utf-8")
    latest = vault_path / "audit_log.md"
    latest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    cleanup_obsidian_vault(vault_path)
    return latest
