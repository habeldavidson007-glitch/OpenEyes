from __future__ import annotations

import json
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich import print
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from openeyes.config import audit_dir, vault_root
from openeyes.services.query_service import QueryService
from openeyes.storage.binary_lib import cleanup_obsidian_vault

LOADING_STAGES = [
    ("Decomposing query...", 0.3),
    ("Retrieving fragments...", 0.4),
    ("Running Monte Carlo verification...", 0.5),
    ("Applying domain rules...", 0.3),
    ("Assembling answer...", 0.3),
]

CLI_SCHEMA_VERSION = "1"


class CLIContext:
    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode


def stream_loading(stages=LOADING_STAGES):
    for message, duration in stages:
        with Live(f"[cyan]⟳ {message}[/cyan]", refresh_per_second=10, transient=True):
            time.sleep(duration)


def typewriter_output(text: str, speed: float = 0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if char in '.!?':
            time.sleep(speed * 8)
        elif char in ',;:':
            time.sleep(speed * 4)
        elif char == '\n':
            time.sleep(speed * 2)
        else:
            time.sleep(speed)
    print()


def emit(ctx: CLIContext, payload: dict, pretty_text: str | None = None, ok: bool = True, error: dict | None = None) -> None:
    if ctx.json_mode:
        data = {
            "ok": ok,
            "cli_schema_version": CLI_SCHEMA_VERSION,
            "data": payload,
            "error": error,
        }
        print(json.dumps(data, indent=2))
        return
    if pretty_text is not None:
        print(pretty_text)
        return
    print(payload)


@click.group()
@click.option("--json", "json_mode", is_flag=True, help="Emit machine-readable JSON for all commands")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool) -> None:
    ctx.obj = CLIContext(json_mode=json_mode)


def _run_query(ctx: CLIContext, query: str, domain: str | None, explain: bool, debug: bool) -> None:
    if not ctx.json_mode:
        stream_loading()

    service = QueryService()
    try:
        result = service.ask(query=query, domain=domain).payload
    except Exception as exc:
        if ctx.json_mode:
            emit(ctx, {}, ok=False, error={"code": "QUERY_EXECUTION_ERROR", "message": str(exc)})
            return
        raise click.ClickException(f"Query failed: {exc}")

    answer_text = result.get("answer", "")
    if ctx.json_mode:
        emit(ctx, result)
        return

    if not explain and not debug:
        typewriter_output(answer_text)
        print(f"\n[cyan]Confidence: {result.get('confidence', 0)}%[/cyan]")
        return

    table = Table(title="OpenEyes Inference (Debug)")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    for k in ["domain", "status", "answer_class", "confidence", "data_recency_years"]:
        table.add_row(k, str(result.get(k)))
    table.add_row("ingested", "YES")
    print(table)
    n = result.get("narrative", {})
    if n:
        print(Panel(json.dumps(n, indent=2), title="Narrative", border_style="blue"))


@cli.command(name="ask")
@click.argument("query")
@click.option("--domain", default=None, help="Optional explicit domain override")
@click.option("--explain", is_flag=True)
@click.option("--debug", is_flag=True)
@click.pass_obj
def ask(ctx: CLIContext, query: str, domain: str | None, explain: bool, debug: bool) -> None:
    _run_query(ctx, query, domain, explain, debug)


@cli.command(name="query", hidden=True)
@click.argument("query")
@click.option("--domain", default=None)
@click.option("--json-output", is_flag=True)
@click.option("--explain", is_flag=True)
@click.option("--debug", is_flag=True)
@click.pass_obj
def query_legacy(ctx: CLIContext, query: str, domain: str | None, json_output: bool, explain: bool, debug: bool) -> None:
    if json_output:
        ctx.json_mode = True
    _run_query(ctx, query, domain, explain, debug)


@cli.command()
@click.pass_obj
def doctor(ctx: CLIContext) -> None:
    vault = vault_root()
    audit = audit_dir()
    checks = {
        "python": sys.version.split()[0],
        "vault_root_exists": vault.exists(),
        "audit_dir_exists": audit.exists(),
        "audit_file_count": len(list(audit.glob("audit_log*.md"))) if audit.exists() else 0,
    }
    emit(ctx, checks)


@cli.command()
@click.pass_obj
def config(ctx: CLIContext) -> None:
    emit(ctx, {"vault_root": str(vault_root()), "audit_dir": str(audit_dir())})


@cli.command()
@click.pass_obj
def version(ctx: CLIContext) -> None:
    emit(ctx, {"version": "0.1.0"}, pretty_text="OpenEyes 0.1.0")


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
