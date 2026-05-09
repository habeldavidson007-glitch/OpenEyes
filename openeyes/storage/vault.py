from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from openeyes.storage.binary_lib import cleanup_obsidian_vault


def write_audit_log(vault_path: Path, query: str, result: dict) -> Path:
    vault_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    payload = {"timestamp": ts, "query": query, "result": result, "version": 1}
    canonical = json.dumps(payload, sort_keys=True)
    signature = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    p = vault_path / f"audit_log_{ts}.md"
    p.write_text(f"# Audit Log\n\nSignature: `{signature}`\n\n```json\n{canonical}\n```\n", encoding="utf-8")
    latest = vault_path / "audit_log.md"
    latest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    cleanup_obsidian_vault(vault_path)
    return latest
