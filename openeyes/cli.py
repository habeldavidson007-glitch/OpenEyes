#!/usr/bin/env python3
"""
OpenEyes CLI - Command Line Interface for the High-Stakes Reasoning Engine
Primary entry point for all OpenEyes operations.
"""

from __future__ import annotations

import json
import sys
import time
import os
from pathlib import Path

# Ensure the package root is in the path
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

from openeyes.config import audit_dir, vault_root
from openeyes.core.engine import OpenEyesEngine
from openeyes.storage.binary_lib import cleanup_obsidian_vault

LOADING_STAGES = [
    ("Decomposing query...", 0.2),
    ("Routing to domain...", 0.15),
    ("Retrieving fragments...", 0.4),
    ("Running Monte Carlo verification...", 0.5),
    ("Applying domain rules...", 0.3),
    ("Assembling answer...", 0.3),
]


def print_banner():
    """Print the OpenEyes ASCII banner."""
    banner = Text("""
┌────────────────────────────────────────────────────────────────────────────────┐
│ 👁️  OPENEYES :: HIGH-STAKES REASONING ENGINE                           │
│                        Command Line Interface                                  │
└────────────────────────────────────────────────────────────────────────────────┘
""", style="bold cyan")
    rprint(banner)


def stream_loading(stages=LOADING_STAGES):
    """Display loading stages with spinner animation."""
    for message, duration in stages:
        with Live(f"[cyan]⟳ {message}[/cyan]", refresh_per_second=10, transient=True) as live:
            time.sleep(duration)


def typewriter_output(text: str, speed: float = 0.015):
    """Print text character by character at human reading pace."""
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


def run_interactive_mode():
    """Run the interactive REPL loop."""
    print_banner()
    rprint("\n[bold green]🚀 Initializing Core Engine...[/bold green]")
    
    try:
        engine = OpenEyesEngine()
    except Exception as e:
        rprint(f"[bold red]❌ Failed to initialize engine: {e}[/bold red]")
        sys.exit(1)
    
    rprint("[bold green]✓ Engine Ready[/bold green]")
    rprint("\n[dim]Type your query or use commands: /help, /stats, /exit[/dim]\n")
    
    while True:
        try:
            user_input = click.prompt("\n👁️  OpenEyes", prompt_suffix="> ", default="", show_default=False).strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                rprint("\n[yellow]Shutting down OpenEyes engine...[/yellow]")
                break
                
            if user_input.lower() == '/help':
                rprint("\n[bold]--- OpenEyes CLI Commands ---[/bold]")
                rprint("  [query]   : Type any question to get an analysis")
                rprint("  /help     : Show this help message")
                rprint("  /stats    : Show system statistics")
                rprint("  /clear    : Clear the screen")
                rprint("  /exit     : Exit the application")
                rprint("-----------------------------\n")
                continue
                
            if user_input.lower() == '/clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_banner()
                continue
                
            if user_input.lower() == '/stats':
                stats = engine.get_statistics() if hasattr(engine, 'get_statistics') else {}
                rprint(f"\n[bold]📊 System Statistics:[/bold]")
                rprint(f"   Total Fragments: {stats.get('total_fragments', 'N/A')}")
                rprint(f"   Domains Active:  {len(stats.get('domain_counts', {}))}")
                for domain, count in stats.get('domain_counts', {}).items():
                    rprint(f"   - [cyan]{domain}[/cyan]: {count}")
                rprint(f"   Memory Priors:   {stats.get('memory_priors', 'N/A')}")
                continue

            rprint("\n[cyan]⏳ Processing...[/cyan]")
            stream_loading()
            
            result = engine.answer(query=user_input)
            
            if result:
                rprint("\n" + "─" * 80)
                confidence = result.get('confidence', 0)
                rprint(f"[bold green]📝 ANSWER ({confidence}% Confidence)[/bold green]")
                rprint("─" * 80)
                typewriter_output(result.get('answer', 'No answer generated.'))
                rprint("─" * 80)
                
                if 'narrative' in result:
                    rprint(f"\n[dim]🔍 Domain: {result.get('domain', 'unknown')}[/dim]")
                    rprint(f"[dim]⏱️  Status: {result.get('status', 'N/A')}[/dim]")
            else:
                rprint("[bold red]❌ No response generated. Try rephrasing your query.[/bold red]")

        except KeyboardInterrupt:
            rprint("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
            break
        except EOFError:
            rprint("\n\n[yellow]EOF received. Exiting...[/yellow]")
            break
        except Exception as e:
            rprint(f"\n[bold red]❌ Error processing query: {str(e)}[/bold red]")
            if os.environ.get('DEBUG'):
                import traceback
                traceback.print_exc()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, version):
    """OpenEyes: High-Stakes Deterministic Chaos Reasoning Engine.
    
    Run without arguments to start interactive mode.
    """
    if version:
        rprint("OpenEyes v1.0.0")
        ctx.exit()
    
    if ctx.invoked_subcommand is None:
        run_interactive_mode()


@cli.command()
@click.argument("query")
@click.option("--domain", default=None, help="Optional explicit domain override")
@click.option("--json-output", is_flag=True, help="Print raw JSON output")
@click.option("--explain", is_flag=True, help="Show inference metadata")
@click.option("--debug", is_flag=True, help="Alias for --explain")
@click.option("--no-banner", is_flag=True, help="Suppress startup banner")
def query_cmd(query: str, domain: str | None, json_output: bool, explain: bool, debug: bool, no_banner: bool):
    """Run a single query and exit."""
    if not no_banner:
        print_banner()
    
    stream_loading()

    try:
        engine = OpenEyesEngine()
        result = engine.answer(query=query, domain=domain)
    except Exception as e:
        rprint(f"[bold red]❌ Error: {e}[/bold red]")
        sys.exit(1)
        
    if json_output:
        print(json.dumps(result, indent=2))
        return

    answer_text = result.get("answer", "")

    if not explain and not debug:
        rprint("\n[bold green]📝 Answer:[/bold green]")
        typewriter_output(answer_text)
        rprint(f"\n[cyan]Confidence: {result.get('confidence', 0)}%[/cyan]")
        return

    if debug or explain:
        table = Table(title="OpenEyes Inference (Debug)")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        for k in ["domain", "status", "answer_class", "confidence", "data_recency_years"]:
            table.add_row(k, str(result.get(k)))
        table.add_row("ingested", "YES")
        rprint(table)
        n = result.get("narrative", {})
        if n:
            rprint(Panel(json.dumps(n, indent=2), title="Narrative", border_style="blue"))


@cli.command()
def sleep():
    """Run consolidation cycle to clean up audit logs."""
    rprint("[yellow]Starting consolidation cycle...[/yellow]")
    cleanup_obsidian_vault(audit_dir())
    rprint("[green]✓ Consolidation complete.[/green]")


@cli.command()
def status():
    """Show system status and statistics."""
    vault = audit_dir()
    files = list(vault.glob("audit_log*.md")) if vault.exists() else []
    stats = {"vault": str(vault_root()), "audit_files": len(files)}
    
    rprint("[bold]System Status:[/bold]")
    for key, value in stats.items():
        rprint(f"  [cyan]{key}[/cyan]: {value}")
    
    try:
        engine = OpenEyesEngine()
        engine_stats = engine.get_statistics() if hasattr(engine, 'get_statistics') else {}
        if engine_stats:
            rprint("\n[bold]Knowledge Base:[/bold]")
            rprint(f"  Total Fragments: {engine_stats.get('total_fragments', 'N/A')}")
            rprint(f"  Domains: {list(engine_stats.get('domain_counts', {}).keys())}")
    except:
        pass


@cli.command()
@click.option("--port", default=8080, type=int, show_default=True)
def serve(port: int):
    """Start API server (placeholder)."""
    rprint(f"[yellow]API placeholder listening on port {port}[/yellow]")


if __name__ == "__main__":
    cli()
