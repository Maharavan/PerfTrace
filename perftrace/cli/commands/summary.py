import click
import psutil
import json
from rich import print
from rich.panel import Panel
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data
from rich.console import Console
import json
import pandas as pd

from perftrace.core.collectors import SystemCollector

def get_collector_value(row, collector, key, default=None):
    raw = row.get(collector)
    if not raw:
        return default
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return data.get(key, default)
    except Exception:
        return default


@click.command(name="summary")
def summary():
    """Show overall performance summary"""

    print(Panel.fit(
        "[bold cyan]PerfTrace Summary[/bold cyan]\nUnified Performance Tracing",
        border_style="cyan"
    ))

    try:
        df = check_retrieve_data()
    except Exception as e:
        print(f"[bold red]Failed to load data:[/bold red] {e}")
        return

    if df.empty:
        print("[yellow]No performance data available[/yellow]")
        return

    df["exec_time"] = df.apply(
        lambda r: get_collector_value(r, "execution_collector", "execution_time"),
        axis=1
    )

    df["memory_mb"] = df.apply(
        lambda r: (
            get_collector_value(r, "memory_collector", "current_memory", 0) / (1024 * 1024)
        ),
        axis=1
    )
    console = Console()

    total_records = len(df)
    functions = df["function_name"].dropna()
    contexts = df["context_tag"].dropna()

    avg_exec = df["exec_time"].mean()
    p95_exec = df["exec_time"].quantile(0.95)

    slowest_row = df.loc[df["exec_time"].idxmax()]
    slowest_name = slowest_row["function_name"] or f"context:{slowest_row['context_tag']}"
    slowest_time = slowest_row["exec_time"]

    most_called_func = functions.value_counts().idxmax()
    most_called_count = functions.value_counts().max()

    slowest_ctx = (
        df.dropna(subset=["context_tag"])
        .groupby("context_tag")["exec_time"]
        .max()
        .idxmax()
        if not contexts.empty else "N/A"
    )

    most_active_ctx = contexts.value_counts().idxmax() if not contexts.empty else "N/A"
    most_active_ctx_calls = contexts.value_counts().max() if not contexts.empty else 0

    avg_mem = df["memory_mb"].mean()
    peak_mem_row = df.loc[df["memory_mb"].idxmax()]
    peak_mem_func = peak_mem_row["function_name"]
    peak_mem_val = peak_mem_row["memory_mb"]
    
    system_data = SystemCollector().report()
    cpu_usage = system_data.get("cpu_percent","")
    mem_usage = system_data.get("memory_percentage","")

    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Records Collected", str(total_records))
    table.add_row("Functions Observed", str(functions.nunique()))
    table.add_row("Contexts Observed", str(contexts.nunique()))

    table.add_row("", "")
    table.add_row("Total Function Calls", str(len(functions)))
    table.add_row("Avg Execution Time", f"{avg_exec*1000:.2f} ms")
    table.add_row("P95 Execution Time", f"{p95_exec*1000:.2f} ms")
    table.add_row("Slowest Execution", f"{slowest_name} ({slowest_time*1000:.2f} ms)")
    table.add_row("Most Called Function", f"{most_called_func} ({most_called_count} calls)")

    table.add_row("", "")
    table.add_row("Total Context Calls", str(len(contexts)))
    table.add_row("Slowest Context", slowest_ctx)
    table.add_row("Most Active Context", f"{most_active_ctx} ({most_active_ctx_calls} calls)")

    table.add_row("", "")
    table.add_row("Avg Memory Usage", f"{avg_mem:.2f} MB")
    table.add_row("Peak Memory Usage", f"{peak_mem_func} ({peak_mem_val:.2f} MB)")

    table.add_row("", "")
    table.add_row("CPU Usage (system)", f"{cpu_usage}%")
    table.add_row("System Memory Usage", f"{mem_usage}%")
    console.print(table)

    verdict = "[green]System looks healthy[/green]"
    if slowest_time > avg_exec * 3:
        verdict = "[yellow]Performance hotspots detected[/yellow]"

    print("\n[bold]Summary Verdict:[/bold]", verdict)