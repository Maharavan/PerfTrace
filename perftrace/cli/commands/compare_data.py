import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import _parse_json, _fmt_time, _fmt_bytes, _fmt_pct, _fmt_mb

console = Console()


def _avg_metrics(df, name, column="function_name"):
    """Return averaged metrics for *name* in *column*, plus the call count."""
    rows = df[df[column] == name]
    if rows.empty:
        return None, 0
    totals = {"exec_time": 0.0, "peak_mem": 0.0, "avg_cpu": 0.0, "ram_delta": 0.0}
    counts = {k: 0 for k in totals}
    for _, row in rows.iterrows():
        exe = _parse_json(row.get("execution_collector"))
        mem = _parse_json(row.get("memory_collector"))
        cpu = _parse_json(row.get("cpu_collector"))
        pairs = [
            ("exec_time", exe.get("execution_time")),
            ("peak_mem",  mem.get("peak_memory")),
            ("avg_cpu",   cpu.get("avg_cpu_percentage")),
            ("ram_delta", cpu.get("ram_delta")),
        ]
        for key, val in pairs:
            try:
                totals[key] += float(val)
                counts[key] += 1
            except (TypeError, ValueError):
                pass
    avgs = {k: (totals[k] / counts[k] if counts[k] else None) for k in totals}
    return avgs, len(rows)


def _render_comparison(label_a, avgs_a, count_a, label_b, avgs_b, count_b, entity_type):
    def _delta_time(va, vb):
        if va is None or vb is None:
            return "—"
        diff = va - vb
        sign = "+" if diff > 0 else ""
        return f"{sign}{_fmt_time(diff)}"

    def _delta_bytes(va, vb):
        if va is None or vb is None:
            return "—"
        diff = va - vb
        sign = "+" if diff > 0 else ""
        return f"{sign}{_fmt_bytes(abs(diff))}"

    table = Table(
        title=f"[bold cyan]{entity_type} Comparison — Average Metrics[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("Metric",                  style="cyan",    no_wrap=True, min_width=20)
    table.add_column(f"{label_a}\n({count_a} runs)", justify="right", style="green")
    table.add_column(f"{label_b}\n({count_b} runs)", justify="right", style="yellow")
    table.add_column("Δ (A − B)",               justify="right", style="magenta")

    table.add_row(
        "Avg Exec Time",
        _fmt_time(avgs_a["exec_time"]),
        _fmt_time(avgs_b["exec_time"]),
        _delta_time(avgs_a["exec_time"], avgs_b["exec_time"]),
    )
    table.add_row(
        "Avg Peak Mem",
        _fmt_bytes(avgs_a["peak_mem"]),
        _fmt_bytes(avgs_b["peak_mem"]),
        _delta_bytes(avgs_a["peak_mem"], avgs_b["peak_mem"]),
    )
    table.add_row("Avg CPU %",  _fmt_pct(avgs_a["avg_cpu"]),  _fmt_pct(avgs_b["avg_cpu"]),  "—")
    table.add_row("Avg RAM Δ",  _fmt_mb(avgs_a["ram_delta"]), _fmt_mb(avgs_b["ram_delta"]), "—")

    console.print(table)


@click.command(name="compare-function")
@click.argument("function_a")
@click.argument("function_b")
def compare_function(function_a, function_b):
    """Compare average performance metrics of two functions side by side.

    \b
    Example:
      perftrace compare-function load_data process_data
    """
    df = check_retrieve_data()
    if df is None or df.empty:
        console.print(Panel("[yellow]No trace data found.[/yellow]", border_style="yellow"))
        return

    avgs_a, count_a = _avg_metrics(df, function_a, column="function_name")
    avgs_b, count_b = _avg_metrics(df, function_b, column="function_name")

    if avgs_a is None:
        console.print(f"[red]No records found for function:[/red] [bold]{function_a}[/bold]")
        return
    if avgs_b is None:
        console.print(f"[red]No records found for function:[/red] [bold]{function_b}[/bold]")
        return

    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]Function Comparison[/dim]",
        border_style="cyan", padding=(0, 2),
    ))
    _render_comparison(function_a, avgs_a, count_a, function_b, avgs_b, count_b, "Function")


@click.command(name="compare-context")
@click.argument("context_a")
@click.argument("context_b")
def compare_context(context_a, context_b):
    """Compare average performance metrics of two context tags side by side.

    \b
    Example:
      perftrace compare-context batch_job import_flow
    """
    df = check_retrieve_data()
    if df is None or df.empty:
        console.print(Panel("[yellow]No trace data found.[/yellow]", border_style="yellow"))
        return

    avgs_a, count_a = _avg_metrics(df, context_a, column="context_tag")
    avgs_b, count_b = _avg_metrics(df, context_b, column="context_tag")

    if avgs_a is None:
        console.print(f"[red]No records found for context:[/red] [bold]{context_a}[/bold]")
        return
    if avgs_b is None:
        console.print(f"[red]No records found for context:[/red] [bold]{context_b}[/bold]")
        return

    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]Context Comparison[/dim]",
        border_style="cyan", padding=(0, 2),
    ))
    _render_comparison(context_a, avgs_a, count_a, context_b, avgs_b, count_b, "Context")
