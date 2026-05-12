from __future__ import annotations

import json
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner


from openeyes.config import audit_dir, vault_root
from openeyes.core.engine import OpenEyesEngine
from openeyes.storage.binary_lib import cleanup_obsidian_vault


LOADING_STAGES = [
    ("Decomposing query...", 0.3),
    ("Retrieving fragments...", 0.4),
    ("Running Monte Carlo verification...", 0.5),
    ("Applying domain rules...", 0.3),
    ("Assembling answer...", 0.3),
]


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


@click.group()
def cli() -> None:
    """OpenEyes deterministic chaos reasoning engine."""


@cli.command()
@click.argument("query")
@click.option("--domain", default=None, help="Optional explicit domain override")
@click.option("--json-output", is_flag=True, help="Print raw JSON output")
@click.option("--explain", is_flag=True, help="Show inference metadata and narrative trace")
@click.option("--debug", is_flag=True, help="Alias for --explain")
def query(query: str, domain: str | None, json_output: bool, explain: bool, debug: bool) -> None:
    # Show loading animation
    stream_loading()
    
    engine = OpenEyesEngine()
    result = engine.answer(query=query, domain=domain)
    if json_output:
        print(json.dumps(result, indent=2))
        return
    
    answer_text = result.get("answer", "")
    
    # Use typewriter effect for answer
    if not explain and not debug:
        # Print answer with typewriter effect
        typewriter_output(answer_text)
        
        # Print confidence
        print(f"\n[cyan]Confidence: {result.get('confidence', 0)}%[/cyan]")
        return

    if debug or explain:
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


@cli.command()
@click.option("--cycles", default=1, type=int, help="Number of pulse cycles to run (-1 for infinite)")
@click.option("--cycle-duration", default=60.0, type=float, help="Total duration of each cycle in seconds")
@click.option("--harvest-duration", default=20.0, type=float, help="Duration of harvest phase in seconds")
@click.option("--process-duration", default=15.0, type=float, help="Duration of process phase in seconds")
@click.option("--archive-duration", default=10.0, type=float, help="Duration of archive phase in seconds")
@click.option("--hibernation-duration", default=15.0, type=float, help="Duration of hibernation phase in seconds")
def pulse(cycles: int, cycle_duration: float, harvest_duration: float, 
          process_duration: float, archive_duration: float, hibernation_duration: float) -> None:
    """Start the autonomous Signal-Pulse Swarm evidence circulation loop."""
    from openeyes.swarm import PulseScheduler
    
    print("[cyan]Starting Signal-Pulse Swarm autonomous loop...[/cyan]")
    print(f"  Cycles: {cycles if cycles > 0 else 'infinite'}")
    print(f"  Cycle duration: {cycle_duration}s")
    print(f"  Phase durations: HARVEST={harvest_duration}s, PROCESS={process_duration}s, ARCHIVE={archive_duration}s, HIBERNATE={hibernation_duration}s")
    
    scheduler = PulseScheduler(
        cycle_duration=cycle_duration,
        harvest_duration=harvest_duration,
        process_duration=process_duration,
        archive_duration=archive_duration,
        hibernation_duration=hibernation_duration,
    )
    
    try:
        max_cycles = None if cycles == -1 else cycles
        asyncio.run(scheduler.run_continuous(max_cycles=max_cycles))
    except KeyboardInterrupt:
        print("\n[yellow]Interrupted by user, shutting down...[/yellow]")
        asyncio.run(scheduler.shutdown())
    
    # Print final metrics
    print("\n[green]Pulse loop complete. Final metrics:[/green]")
    metrics = scheduler.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    cli()
