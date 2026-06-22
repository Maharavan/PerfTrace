import click
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import _fmt_bytes, _fmt_pct, _parse_json

console = Console()


@click.command(name="top-memory")
@click.option("--limit", "-n", default=10, show_default=True, help="Number of entries to show.")
def top_memory(limit):
    """Show top N functions/contexts ranked by peak memory allocation."""
    df = check_retrieve_data()
    if df.empty:
        console.print("[red]No trace data found.[/red]")
        return

    agg = defaultdict(lambda: {"peak": 0.0, "current": 0.0, "kind": "function"})

    for _, row in df.iterrows():
        name = row.get("function_name") or row.get("context_tag")
        if not name or name == "-":
            continue
        mem = _parse_json(row.get("memory_collector"))
        try:
            peak = float(mem.get("peak_memory") or 0)
            current = float(mem.get("current_memory") or 0)
            if peak > agg[str(name)]["peak"]:
                agg[str(name)]["peak"] = peak
                agg[str(name)]["current"] = current
                agg[str(name)]["kind"] = "function" if row.get("function_name") else "context"
        except (ValueError, TypeError):
            pass

    if not agg:
        console.print("[yellow]No memory data available. Ensure the memory collector is enabled.[/yellow]")
        return

    ranked = sorted(agg.items(), key=lambda x: x[1]["peak"], reverse=True)[:limit]

    table = Table(
        title=f"[bold cyan]Top {limit} — Peak Memory Usage[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Name", style="green")
    table.add_column("Type", style="dim", width=10)
    table.add_column("Current Mem", justify="right", style="blue")
    table.add_column("Peak Mem", justify="right", style="magenta")

    for i, (name, vals) in enumerate(ranked, 1):
        table.add_row(
            str(i),
            name,
            vals["kind"],
            _fmt_bytes(vals["current"]),
            _fmt_bytes(vals["peak"]),
        )

    console.print(table)


@click.command(name="top-cpu")
@click.option("--limit", "-n", default=10, show_default=True, help="Number of entries to show.")
def top_cpu(limit):
    """Show top N functions/contexts ranked by average CPU usage."""
    df = check_retrieve_data()
    if df.empty:
        console.print("[red]No trace data found.[/red]")
        return

    agg = defaultdict(list)
    kinds = {}

    for _, row in df.iterrows():
        name = row.get("function_name") or row.get("context_tag")
        if not name or name == "-":
            continue
        cpu = _parse_json(row.get("cpu_collector"))
        avg_cpu = cpu.get("avg_cpu_percentage")
        try:
            agg[str(name)].append(float(avg_cpu))
            kinds[str(name)] = "function" if row.get("function_name") else "context"
        except (ValueError, TypeError):
            pass

    if not agg:
        console.print("[yellow]No CPU data available. Ensure the cpu collector is enabled.[/yellow]")
        return

    ranked = sorted(
        [(name, sum(vals) / len(vals), kinds[name]) for name, vals in agg.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:limit]

    table = Table(
        title=f"[bold cyan]Top {limit} — Average CPU Usage[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Name", style="green")
    table.add_column("Type", style="dim", width=10)
    table.add_column("Avg CPU %", justify="right", style="yellow")

    for i, (name, avg, kind) in enumerate(ranked, 1):
        table.add_row(str(i), name, kind, _fmt_pct(avg))

    console.print(table)
