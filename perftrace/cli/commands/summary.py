import click
import json
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.core.collectors import SystemCollector

console = Console()


def _get(row, collector, key, default=None):
    raw = row.get(collector)
    if not raw:
        return default
    try:
        d = json.loads(raw) if isinstance(raw, str) else raw
        return d.get(key, default)
    except Exception:
        return default


def _fmt_ms(seconds):
    if seconds is None:
        return "-"
    try:
        ms = float(seconds) * 1000
        return f"{ms:.2f} ms"
    except (TypeError, ValueError):
        return "-"


def _fmt_mb(b):
    if b is None:
        return "-"
    try:
        return f"{float(b) / (1024 * 1024):.2f} MB"
    except (TypeError, ValueError):
        return "-"


def _pct_color(pct):
    try:
        p = float(pct)
        if p >= 80:
            return "bold red"
        if p >= 50:
            return "yellow"
        return "green"
    except (TypeError, ValueError):
        return "white"


def _section(title, color="cyan"):
    t = Table(
        title=f"[bold {color}]{title}[/bold {color}]",
        show_header=True,
        header_style=f"bold {color}",
        show_lines=False,
        border_style=f"dim {color}",
        padding=(0, 1),
        expand=True,
    )
    t.add_column("Metric", style="cyan",  no_wrap=True, min_width=28)
    t.add_column("Value",  style="white", overflow="fold")
    return t


@click.command(name="summary")
def summary():
    """Show a color-coded overall performance and system summary."""
    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]Performance Summary[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    try:
        df = check_retrieve_data()
    except Exception as e:
        console.print(f"[bold red]Failed to load data:[/bold red] {e}")
        return

    if df.empty:
        console.print(Panel("[yellow]No performance data recorded yet.[/yellow]",
                            border_style="yellow"))
        return

    df["exec_time"] = df.apply(
        lambda r: _get(r, "execution_collector", "execution_time"), axis=1
    )
    df["memory_bytes"] = df.apply(
        lambda r: _get(r, "memory_collector", "current_memory", 0), axis=1
    )

    functions = df["function_name"].dropna()
    contexts  = df["context_tag"].dropna()

    # ── Records overview ──────────────────────────────────────────────────────
    t_rec = _section("Records", "cyan")
    t_rec.add_row("Total Records",       f"[white]{len(df):,}[/white]")
    t_rec.add_row("Unique Functions",    f"[white]{functions.nunique():,}[/white]")
    t_rec.add_row("Unique Contexts",     f"[white]{contexts.nunique():,}[/white]")
    t_rec.add_row("Total Function Calls", f"[white]{len(functions):,}[/white]")
    t_rec.add_row("Total Context Calls", f"[white]{len(contexts):,}[/white]")
    console.print(t_rec)

    # ── Execution timing ──────────────────────────────────────────────────────
    exec_clean = df["exec_time"].dropna()
    if not exec_clean.empty:
        avg_exec = exec_clean.mean()
        p95_exec = exec_clean.quantile(0.95)
        p99_exec = exec_clean.quantile(0.99)
        max_idx  = exec_clean.idxmax()
        min_idx  = exec_clean.idxmin()

        slowest_name = df.loc[max_idx, "function_name"] or f"context:{df.loc[max_idx, 'context_tag']}"
        fastest_name = df.loc[min_idx, "function_name"] or f"context:{df.loc[min_idx, 'context_tag']}"

        avg_col = _pct_color(avg_exec * 1000 / 10)

        t_exec = _section("Execution Timing", "yellow")
        t_exec.add_row("Avg Execution",    f"[{avg_col}]{_fmt_ms(avg_exec)}[/{avg_col}]")
        t_exec.add_row("p95 Execution",    f"[yellow]{_fmt_ms(p95_exec)}[/yellow]")
        t_exec.add_row("p99 Execution",    f"[yellow]{_fmt_ms(p99_exec)}[/yellow]")
        t_exec.add_row("Slowest",          f"[red]{slowest_name}[/red]  "
                                           f"[dim]{_fmt_ms(exec_clean[max_idx])}[/dim]")
        t_exec.add_row("Fastest",          f"[green]{fastest_name}[/green]  "
                                           f"[dim]{_fmt_ms(exec_clean[min_idx])}[/dim]")

        if not functions.empty:
            most_called_func  = functions.value_counts().idxmax()
            most_called_count = functions.value_counts().max()
            t_exec.add_section()
            t_exec.add_row("Most Called Function",
                           f"[cyan]{most_called_func}[/cyan]  "
                           f"[dim]{most_called_count:,} calls[/dim]")

        if not contexts.empty:
            most_active_ctx   = contexts.value_counts().idxmax()
            most_active_count = contexts.value_counts().max()
            t_exec.add_row("Most Active Context",
                           f"[cyan]{most_active_ctx}[/cyan]  "
                           f"[dim]{most_active_count:,} calls[/dim]")

        console.print(t_exec)

    # ── Memory ────────────────────────────────────────────────────────────────
    mem_clean = df["memory_bytes"].dropna()
    if not mem_clean.empty:
        avg_mem   = mem_clean.mean()
        peak_idx  = mem_clean.idxmax()
        peak_func = df.loc[peak_idx, "function_name"] or f"context:{df.loc[peak_idx, 'context_tag']}"
        peak_val  = mem_clean[peak_idx]

        t_mem = _section("Memory", "blue")
        t_mem.add_row("Avg Memory Usage",  f"[blue]{_fmt_mb(avg_mem)}[/blue]")
        t_mem.add_row("Peak Memory",       f"[bold red]{_fmt_mb(peak_val)}[/bold red]")
        t_mem.add_row("Peak in",           f"[white]{peak_func}[/white]")
        console.print(t_mem)

    # ── Live system ───────────────────────────────────────────────────────────
    try:
        sys_data   = SystemCollector().report()
        cpu_usage  = sys_data.get("cpu_percent", 0)
        mem_usage  = sys_data.get("memory_percentage", 0)
        cpu_col    = _pct_color(cpu_usage)
        mem_col    = _pct_color(mem_usage)

        t_sys = _section("Live System", "green")
        t_sys.add_row("CPU Usage",      f"[{cpu_col}]{cpu_usage:.1f}%[/{cpu_col}]")
        t_sys.add_row("Memory Usage",   f"[{mem_col}]{mem_usage:.1f}%[/{mem_col}]")
        console.print(t_sys)
    except Exception:
        pass

    # ── Verdict ───────────────────────────────────────────────────────────────
    hotspot = (not exec_clean.empty) and (exec_clean.max() > exec_clean.mean() * 3)
    if hotspot:
        verdict = "[bold yellow]Performance hotspots detected[/bold yellow]"
        border  = "yellow"
    else:
        verdict = "[bold green]System looks healthy[/bold green]"
        border  = "green"

    console.print(Panel.fit(verdict, border_style=border, padding=(0, 2)))
