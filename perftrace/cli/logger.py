from collections import defaultdict
import json
import pandas as pd
from rich import print
from rich.console import Console
from rich.table import Table
import numpy as np


console = Console()

# ── Value formatters ──────────────────────────────────────────────────────────

def _fmt_time(seconds):
    """Format a duration in seconds to a human-readable string."""
    if seconds is None:
        return "-"
    try:
        s = float(seconds)
    except (TypeError, ValueError):
        return str(seconds)
    if s == 0:
        return "0 s"
    if abs(s) < 0.001:
        return f"{s * 1_000_000:.2f} µs"
    if abs(s) < 1:
        return f"{s * 1_000:.3f} ms"
    return f"{s:.4f} s"


def _fmt_bytes(b):
    """Format a byte count to B / KB / MB / GB."""
    if b is None:
        return "-"
    try:
        b = float(b)
    except (TypeError, ValueError):
        return str(b)
    if abs(b) < 1024:
        return f"{b:.0f} B"
    if abs(b) < 1024 ** 2:
        return f"{b / 1024:.2f} KB"
    if abs(b) < 1024 ** 3:
        return f"{b / 1024 ** 2:.2f} MB"
    return f"{b / 1024 ** 3:.2f} GB"


def _fmt_mb(v):
    """Format a value that is already in MB, with sign."""
    if v is None:
        return "-"
    try:
        f = float(v)
        sign = "+" if f > 0 else ""
        return f"{sign}{f:.3f} MB"
    except (TypeError, ValueError):
        return str(v)


def _fmt_pct(v):
    """Format a percentage value."""
    if v is None:
        return "-"
    try:
        return f"{float(v):.1f}%"
    except (TypeError, ValueError):
        return str(v)


def _fmt_num(v, dp=4):
    """Format a generic number to dp decimal places."""
    if v is None:
        return "-"
    try:
        return f"{float(v):.{dp}f}"
    except (TypeError, ValueError):
        return str(v)


def _parse_json(val):
    """Safely parse a JSON string or return {} / the value itself."""
    if val in (None, "-", ""):
        return {}
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return {}
    if isinstance(val, dict):
        return val
    return {}


def _trim_ts(ts):
    """Remove sub-second precision from a timestamp string."""
    s = str(ts)
    if "." in s:
        s = s.rsplit(".", 1)[0]
    return s


# ── Multi-record compact table (used by show-function / show-context) ─────────

def get_compact_trace_table(dataframe):
    """
    Render all records as a single wide summary table.
    One row per trace record; columns cover the key metrics.
    """
    if dataframe.empty:
        console.print("[red]Empty result. Please provide a valid command.[/red]")
        return

    first = dataframe.iloc[0]
    fn = first.get("function_name")
    ct = first.get("context_tag")
    name = fn if fn not in (None, "-", "", "N/A") else ct
    count = len(dataframe)

    table = Table(
        title=f"[bold cyan]{name}[/bold cyan]  [dim]({count} record{'s' if count != 1 else ''})[/dim]",
        show_lines=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("#",          justify="right",  style="dim",     no_wrap=True, width=4)
    table.add_column("Timestamp",  style="white",    no_wrap=True)
    table.add_column("Exec Time",  justify="right",  style="green",   no_wrap=True)
    table.add_column("Peak Mem",   justify="right",  style="blue",    no_wrap=True)
    table.add_column("RAM Δ",      justify="right",  style="blue",    no_wrap=True)
    table.add_column("CPU %",      justify="right",  style="yellow",  no_wrap=True)
    table.add_column("Threads Δ",  justify="right",  style="magenta", no_wrap=True)
    table.add_column("Status",     justify="center", style="white",   no_wrap=True)

    for idx, (_, row) in enumerate(dataframe.iterrows(), 1):
        exc  = _parse_json(row.get("exception_collector"))
        mem  = _parse_json(row.get("memory_collector"))
        cpu  = _parse_json(row.get("cpu_collector"))
        exe  = _parse_json(row.get("execution_collector"))
        thrd = _parse_json(row.get("thread_context_collector"))

        occurred = exc.get("occurred", False)
        if occurred:
            exc_type = exc.get("exception_type", "Error")
            status = f"[bold red]⚠ {exc_type}[/bold red]"
        else:
            status = "[green]✓ OK[/green]"

        ram_delta = cpu.get("ram_delta")
        ram_str   = _fmt_mb(ram_delta)
        if ram_delta is not None:
            try:
                ram_str = f"[red]{ram_str}[/red]" if float(ram_delta) > 1 else f"[green]{ram_str}[/green]"
            except (TypeError, ValueError):
                pass

        threads_delta = thrd.get("threads_delta")

        table.add_row(
            str(idx),
            _trim_ts(row.get("timestamp", "-")),
            _fmt_time(exe.get("execution_time")),
            _fmt_bytes(mem.get("peak_memory")),
            ram_str,
            _fmt_pct(cpu.get("avg_cpu_percentage")),
            str(threads_delta) if threads_delta is not None else "-",
            status,
        )

    console.print(table)


# ── Single-record deep table (used by recent-function / recent-context) ───────

def get_recent_info_about_function_context(dataframe):
    """Display a detailed breakdown of a single trace record."""
    if dataframe.empty:
        console.print("[red]Empty result. Please provide a valid command.[/red]")
        return

    # Pretty-print each metric's dict with formatted values
    _BYTE_KEYS = {
        "peak_memory", "current_memory",
        "read_bytes", "write_bytes", "other_bytes",
        "bytes_sent", "bytes_received",
        "bytes_sent_delta", "bytes_received_delta",
        "total_system_memory", "available_system_memory",
        "used_memory", "free_memory",
        "total_disk_space", "used_disk_space", "free_disk_space",
    }
    _TIME_KEYS  = {"execution_time", "start_time", "end_time"}
    _PCT_KEYS   = {"avg_cpu_percentage", "cpu_usage_start", "cpu_usage_end", "memory_percentage", "cpu_percent"}
    _MB_KEYS    = {"ram_delta", "start_ram", "end_ram"}

    def _fmt_val(key, val):
        if val is None:
            return "—"
        if key in _TIME_KEYS:
            return _fmt_time(val)
        if key in _BYTE_KEYS:
            return _fmt_bytes(val)
        if key in _PCT_KEYS:
            return _fmt_pct(val)
        if key in _MB_KEYS:
            return _fmt_mb(val)
        if isinstance(val, float):
            return _fmt_num(val, dp=4)
        return str(val)

    for _, row in dataframe.iterrows():
        func_name = row.get("function_name", "N/A")
        ctx_tag   = row.get("context_tag", "N/A")
        timestamp = row.get("timestamp", "N/A")
        tit_header = func_name if func_name not in ("N/A", None, "-") else ctx_tag

        table = Table(
            title=f"[bold]Trace Report — {tit_header}[/bold]",
            show_lines=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("Metric", style="cyan",    no_wrap=True, min_width=28)
        table.add_column("Value",  style="magenta", overflow="fold")

        if func_name not in (None, "-"):
            table.add_row("Function Name", str(func_name))
        if ctx_tag not in (None, "-"):
            table.add_row("Context Tag", str(ctx_tag))
        table.add_row("Timestamp", _trim_ts(timestamp))
        table.add_section()

        exception_data = None

        for metric, results in row.items():
            if metric in ("timestamp", "function_name", "context_tag"):
                continue
            if results in (None, "-", ""):
                continue
            try:
                parsed = json.loads(results) if isinstance(results, str) else results
                if metric == "exception_collector":
                    exception_data = parsed
                    continue
                if isinstance(parsed, dict):
                    formatted = "\n".join(
                        f"[dim]{k}:[/dim]  {_fmt_val(k, v)}" for k, v in parsed.items()
                    )
                    table.add_row(metric, formatted)
                else:
                    table.add_row(metric, str(parsed))
            except Exception:
                table.add_row(metric, str(results))

        table.add_section()
        if exception_data and isinstance(exception_data, dict):
            if exception_data.get("occurred"):
                exc_lines = (
                    f"[bold red]Type:[/bold red]    {exception_data.get('exception_type', 'N/A')}\n"
                    f"[bold red]Message:[/bold red] {exception_data.get('exception_message', 'N/A')}\n"
                    f"[dim]{(exception_data.get('traceback') or '').strip()}[/dim]"
                )
                table.add_row("[bold red]Exception[/bold red]", exc_lines)
            else:
                table.add_row("Exception", "[green]✓ None[/green]")

        console.print(table)


# ── Statistical summary ───────────────────────────────────────────────────────

def statistical_summary(dataframe):
    """Generate statistical summary (min, max, avg) for JSON metrics."""
    if dataframe.empty:
        console.print("[red]Empty result. Please provide a valid command.[/red]")
        return

    dataframe_modified = dataframe.drop(
        ['timestamp', 'function_name', 'context_tag'], axis=1, errors="ignore"
    )
    max_collector = defaultdict(lambda: float('-inf'))
    min_collector = defaultdict(lambda: float('inf'))
    avg_collector = defaultdict(list)

    for col in dataframe_modified.columns:
        for val in dataframe_modified[col]:
            if val in (None, '-', ''):
                continue
            try:
                val_dict = json.loads(val) if isinstance(val, str) else val
                if not isinstance(val_dict, dict):
                    continue
            except Exception:
                continue
            for key, data in val_dict.items():
                if isinstance(data, (int, float)):
                    max_collector[key] = max(max_collector[key], data)
                    min_collector[key] = min(min_collector[key], data)
                    avg_collector[key].append(data)

    summary = {}
    for key in avg_collector:
        values = avg_collector[key]
        summary[key] = {
            "min":     round(min_collector[key], 4),
            "max":     round(max_collector[key], 4),
            "avg":     round(sum(values) / len(values), 4) if values else None,
            "std_dev": round(np.std(values), 4) if len(values) > 1 else None,
            "p90":     round(np.percentile(values, 90), 4) if len(values) > 1 else None,
            "p95":     round(np.percentile(values, 95), 4) if len(values) > 1 else None,
            "p99":     round(np.percentile(values, 99), 4) if len(values) > 1 else None,
        }

    table = Table(
        title="[bold cyan]PerfTrace Statistical Summary[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Metric",   style="cyan",    no_wrap=True)
    table.add_column("Min",      justify="right", style="green")
    table.add_column("Max",      justify="right", style="red")
    table.add_column("Avg",      justify="right", style="blue")
    table.add_column("Std Dev",  justify="right", style="dim")
    table.add_column("p90",      justify="right", style="yellow")
    table.add_column("p95",      justify="right", style="yellow")
    table.add_column("p99",      justify="right", style="yellow")

    def sv(v):
        return str(v) if v is not None else "—"

    for metric, vals in summary.items():
        table.add_row(
            metric,
            sv(vals['min']),
            sv(vals['max']),
            sv(vals['avg']),
            sv(vals['std_dev']),
            sv(vals['p90']),
            sv(vals['p95']),
            sv(vals['p99']),
        )

    console.print(table)


# ── Slowest / fastest ─────────────────────────────────────────────────────────

def find_slowest_fastest_executed(dataframe, column_name, sort_by=True):
    """Display top 10 slowest / fastest executed functions or contexts."""
    title = 'Fastest Executions' if sort_by else 'Slowest Executions'
    df_clean = dataframe.dropna(subset=[column_name])
    output = defaultdict(float)

    for _, row in df_clean.iterrows():
        collector = row["execution_collector"]
        if isinstance(collector, str):
            collector = json.loads(collector)
        output[str(row[column_name])] += float(collector["execution_time"])

    df_output = pd.DataFrame(list(output.items()), columns=[column_name, 'execution_time'])
    df_output = df_output.sort_values(by='execution_time', ascending=sort_by).head(10)

    table = Table(title=f"[bold cyan]{title}[/bold cyan]", header_style="bold cyan", border_style="dim")
    table.add_column(column_name,    style="green")
    table.add_column("Exec Time",    justify="right", style="blue")

    for _, row in df_output.iterrows():
        table.add_row(str(row[column_name]), _fmt_time(row['execution_time']))

    console.print(table)


# ── Filter and list unique function names / context tags ─────────────────────

def filter_functions_context(dataframe, column_name):
    """Display unique entries for a given column (function_name or context_tag)."""
    label = "Function Name" if column_name == "function_name" else "Context Tag"
    df_filtered = dataframe.dropna(subset=[column_name])
    df_filtered = df_filtered[df_filtered[column_name].astype(str).str.strip() != ""]

    if df_filtered.empty:
        console.print(f"[dim]  No {label.lower()} records found.[/dim]")
        return

    counts = df_filtered[column_name].value_counts()

    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        show_lines=False,
    )
    table.add_column(label,  style="green",  no_wrap=True)
    table.add_column("Calls", justify="right", style="blue", no_wrap=True)

    for name, count in counts.items():
        table.add_row(str(name), str(count))

    console.print(table)


# ── Memory breakdown ──────────────────────────────────────────────────────────

def inverted_print(dataframe_modified, header_row, column):
    if dataframe_modified.empty:
        console.print("[red]Empty result. Please provide a valid command.[/red]")
        return

    table = Table(
        title="[bold cyan]Memory Usage[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column(header_row,       justify="center", style="green")
    table.add_column("Current Memory", justify="right",  style="cyan")
    table.add_column("Peak Memory",    justify="right",  style="magenta")

    merged = defaultdict(lambda: {"current_memory": None, "peak_memory": None})

    for _, row in dataframe_modified.iterrows():
        if row[header_row] is None or row[column] in (None, "-", ""):
            continue
        try:
            mem_values = json.loads(row[column]) if isinstance(row[column], str) else row[column]
        except Exception:
            continue
        if not isinstance(mem_values, dict):
            continue
        name = str(row[header_row])
        current = mem_values.get("current_memory")
        peak    = mem_values.get("peak_memory")
        if current is not None:
            existing = merged[name]["current_memory"]
            merged[name]["current_memory"] = current if existing is None else max(existing, current)
        if peak is not None:
            existing = merged[name]["peak_memory"]
            merged[name]["peak_memory"] = peak if existing is None else max(existing, peak)

    for name, vals in merged.items():
        table.add_row(
            name,
            _fmt_bytes(vals.get("current_memory")),
            _fmt_bytes(vals.get("peak_memory")),
        )

    console.print(table)
