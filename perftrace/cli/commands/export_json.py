import os
import uuid
import click
from rich.console import Console
from rich.panel import Panel
from perftrace.cli.db_utils import check_retrieve_data

console = Console()
RANDOM_ID = uuid.uuid4()


def _export_json(df, filename, label, limit=None):
    if not filename.endswith(".json"):
        filename += ".json"

    if df.empty:
        console.print(f"[yellow]No {label} data found to export.[/yellow]")
        return

    if limit is not None:
        df = df.head(limit)

    df.to_json(filename, orient="records", indent=4)

    abs_path = os.path.abspath(filename)
    size_kb = os.path.getsize(abs_path) / 1024
    console.print(Panel.fit(
        f"[bold green]JSON export successful[/bold green]\n"
        f"[cyan]File:[/cyan]  {abs_path}\n"
        f"[cyan]Rows:[/cyan]  {len(df)}\n"
        f"[cyan]Size:[/cyan]  {size_kb:.1f} KB",
        title=f"[bold]{label} Export[/bold]",
        border_style="green"
    ))


@click.command(name="export-json")
@click.option("--filename", default=f"perftrace_all_{RANDOM_ID}.json", help="Output JSON filename")
@click.option("--limit", type=int, default=None, help="Limit number of rows")
def export_all_json(filename, limit):
    """Export complete PerfTrace database to JSON."""
    try:
        df = check_retrieve_data()
        _export_json(df, filename, "All Data", limit)
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")


@click.command(name="export-function-json")
@click.option("--filename", default=f"perftrace_function_{RANDOM_ID}.json", help="Output JSON filename")
@click.option("--limit", type=int, default=None, help="Limit number of rows")
def export_function_json(filename, limit):
    """Export function-level trace records to JSON."""
    try:
        df = check_retrieve_data()
        df = df.dropna(subset=["function_name"])
        _export_json(df, filename, "Function", limit)
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")


@click.command(name="export-context-json")
@click.option("--filename", default=f"perftrace_context_{RANDOM_ID}.json", help="Output JSON filename")
@click.option("--limit", type=int, default=None, help="Limit number of rows")
def export_context_json(filename, limit):
    """Export context manager trace records to JSON."""
    try:
        df = check_retrieve_data()
        df = df.dropna(subset=["context_tag"])
        _export_json(df, filename, "Context", limit)
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")
