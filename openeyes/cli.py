from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich import print
from rich.panel import Panel
from rich.table import Table


from openeyes.config import audit_dir, vault_root
from openeyes.core.engine import OpenEyesEngine
from openeyes.storage.binary_lib import cleanup_obsidian_vault


@click.group()
def cli() -> None:
    """OpenEyes deterministic chaos reasoning engine."""


@cli.command()
@click.argument("query")
@click.option("--domain", default=None, help="Optional explicit domain override")
@click.option("--json-output", is_flag=True, help="Print raw JSON output")
def query(query: str, domain: str | None, json_output: bool) -> None:
    engine = OpenEyesEngine()
    result = engine.answer(query=query, domain=domain)
    if json_output:
        print(json.dumps(result, indent=2))
        return
    table = Table(title="OpenEyes Inference")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    for k in ["domain", "status", "answer_class", "confidence"]:
        table.add_row(k, str(result.get(k)))
    print(table)
    print(Panel(result.get("answer", ""), title="Answer", border_style="green"))


@cli.command()
def sleep() -> None:
    cleanup_obsidian_vault(audit_dir())
    print("[green]Consolidation complete.[/green]")


@cli.command()
def status() -> None:
    vault = audit_dir()
    files = list(vault.glob("audit_log*.md")) if vault.exists() else []
    print({"vault": str(vault_root()), "audit_files": len(files)})


@cli.command()
@click.option("--port", default=8080, type=int, show_default=True)
def serve(port: int) -> None:
    print(f"API placeholder listening on port {port}")


if __name__ == "__main__":
    cli()
