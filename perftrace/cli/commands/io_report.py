import click
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import _fmt_bytes, _parse_json

console = Console()


@click.command(name="io-report")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of entries to show.")
def io_report(limit):
    """Show aggregated file I/O (read/write bytes and op counts) per function/context."""
    df = check_retrieve_data()
    if df.empty:
        console.print("[red]No trace data found.[/red]")
        return

    agg = defaultdict(lambda: {"read": 0.0, "write": 0.0, "read_ops": 0, "write_ops": 0, "kind": "function"})

    for _, row in df.iterrows():
        name = row.get("function_name") or row.get("context_tag")
        if not name or name == "-":
            continue
        io = _parse_json(row.get("file_io_collector"))
        try:
            n = str(name)
            agg[n]["read"]      += float(io.get("read_bytes",  0) or 0)
            agg[n]["write"]     += float(io.get("write_bytes", 0) or 0)
            agg[n]["read_ops"]  += int(io.get("read_count",   0) or 0)
            agg[n]["write_ops"] += int(io.get("write_count",  0) or 0)
            agg[n]["kind"] = "function" if row.get("function_name") else "context"
        except (ValueError, TypeError):
            pass

    data = sorted(agg.items(), key=lambda x: x[1]["read"] + x[1]["write"], reverse=True)[:limit]

    if not data or all(v["read"] == 0 and v["write"] == 0 for _, v in data):
        console.print("[yellow]No file I/O data available. Ensure the file collector is enabled.[/yellow]")
        return

    table = Table(
        title=f"[bold cyan]File I/O Report — Top {limit}[/bold cyan]",
        header_style="bold cyan",
        border_style="dim",
        show_lines=True,
    )
    table.add_column("#",          justify="right", style="dim",    width=4)
    table.add_column("Name",       style="green")
    table.add_column("Type",       style="dim",    width=10)
    table.add_column("Read",       justify="right", style="blue")
    table.add_column("Write",      justify="right", style="yellow")
    table.add_column("Read Ops",   justify="right", style="blue")
    table.add_column("Write Ops",  justify="right", style="yellow")

    for i, (name, vals) in enumerate(data, 1):
        table.add_row(
            str(i),
            name,
            vals["kind"],
            _fmt_bytes(vals["read"]),
            _fmt_bytes(vals["write"]),
            str(vals["read_ops"]),
            str(vals["write_ops"]),
        )

    console.print(table)
