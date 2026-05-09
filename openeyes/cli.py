from __future__ import annotations

import json
from pathlib import Path

import click
from rich import print

from openeyes.config import audit_dir, vault_root
from openeyes.core.engine import OpenEyesEngine
from openeyes.storage.binary_lib import cleanup_obsidian_vault


@click.group()
def cli() -> None:
    """OpenEyes deterministic chaos reasoning engine."""


@cli.command()
@click.argument("query")
@click.option("--domain", default="medical", show_default=True)
def query(query: str, domain: str) -> None:
    engine = OpenEyesEngine()
    result = engine.answer(query=query, domain=domain)
    print(json.dumps(result, indent=2))


@cli.command()
def sleep() -> None:
    cleanup_obsidian_vault(audit_dir())
    print("[green]Consolidation complete.[/green]")


@cli.command()
def status() -> None:
    vault = vault_root()
    files = list(vault.glob("*.md")) if vault.exists() else []
    print({"vault": str(vault), "audit_files": len(files)})


@cli.command()
@click.option("--port", default=8080, type=int, show_default=True)
def serve(port: int) -> None:
    print(f"API placeholder listening on port {port}")


if __name__ == "__main__":
    cli()
