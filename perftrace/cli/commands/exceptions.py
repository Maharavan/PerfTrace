import click
from rich.console import Console
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import _parse_json, _fmt_time, _trim_ts

console = Console()


@click.command(name="exceptions")
@click.option("--limit", "-n", default=50, show_default=True, help="Maximum records to display.")
def exceptions(limit):
    """List all trace records where an exception was raised."""
    df = check_retrieve_data()
    if df.empty:
        console.print("[red]No trace data found.[/red]")
        return

    rows = []
    for _, row in df.iterrows():
        exc = _parse_json(row.get("exception_collector"))
        if not exc.get("occurred", False):
            continue
        exe = _parse_json(row.get("execution_collector"))
        name = row.get("function_name") or row.get("context_tag") or "unknown"
        kind = "function" if row.get("function_name") else "context"
        rows.append({
            "ts":       row.get("timestamp", "-"),
            "name":     str(name),
            "kind":     kind,
            "exec_time": exe.get("execution_time"),
            "exc_type": exc.get("exception_type", "Error"),
            "exc_msg":  (str(exc.get("exception_message") or ""))[:80],
        })

    if not rows:
        console.print("[green]No exceptions found — all traces completed successfully.[/green]")
        return

    rows = rows[:limit]
    table = Table(
        title=f"[bold red]Exception Traces ({len(rows)} record{'s' if len(rows) != 1 else ''})[/bold red]",
        header_style="bold red",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("Timestamp",      style="white",  no_wrap=True)
    table.add_column("Name",           style="yellow")
    table.add_column("Type",           style="dim",   width=10)
    table.add_column("Exec Time",      justify="right", style="green")
    table.add_column("Exception Type", style="red")
    table.add_column("Message",        style="dim",   overflow="fold")

    for r in rows:
        table.add_row(
            _trim_ts(r["ts"]),
            r["name"],
            r["kind"],
            _fmt_time(r["exec_time"]),
            r["exc_type"],
            r["exc_msg"],
        )

    console.print(table)
