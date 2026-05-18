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
    def __init__(self, json_mode: bool = False, no_animate: bool = False, fast: bool = False):
        self.json_mode = json_mode
        self.no_animate = no_animate
        self.fast = fast


def stream_loading(stages=LOADING_STAGES, fast: bool = False):
    if not sys.stdout.isatty():
        return
    speed_factor = 0.35 if fast else 1.0
    for message, duration in stages:
        with Live(f"[cyan]⟳ {message}[/cyan]", refresh_per_second=20, transient=True):
            time.sleep(duration * speed_factor)


def typewriter_output(text: str, speed: float = 0.012):
    if not sys.stdout.isatty():
        print(text)
        return
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if char in ".!?":
            time.sleep(speed * 5)
        elif char in ",;:":
            time.sleep(speed * 3)
        elif char == "\n":
            time.sleep(speed * 1.5)
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
@click.option("--no-animate", is_flag=True, help="Disable loading and typewriter animations")
@click.option("--fast", is_flag=True, help="Speed up animations for quick terminal feedback")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool, no_animate: bool, fast: bool) -> None:
    ctx.obj = CLIContext(json_mode=json_mode, no_animate=no_animate, fast=fast)


def _run_query(ctx: CLIContext, query: str, domain: str | None, explain: bool, debug: bool) -> None:
    if not ctx.json_mode and not ctx.no_animate:
        stream_loading(fast=ctx.fast)

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
        if ctx.no_animate:
            print(answer_text)
        else:
            typewriter_output(answer_text, speed=0.006 if ctx.fast else 0.012)
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
@click.option("--domain", default=None, help="Optional override; OpenEyes auto-routes domain by default")
@click.option("--explain", is_flag=True, help="Show inference metadata and narrative trace")
@click.option("--debug", is_flag=True, help="Alias for --explain")
@click.pass_obj
def ask(ctx: CLIContext, query: str, domain: str | None, explain: bool, debug: bool) -> None:
    _run_query(ctx, query, domain, explain, debug)


@cli.command(name="query", hidden=True)
@click.argument("query")
@click.option("--domain", default=None, help="Optional override; OpenEyes auto-routes domain by default")
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
