import click
from perftrace.cli.logger import get_compact_trace_table
from perftrace.cli.db_utils import check_retrieve_data
from rich.console import Console
from rich.panel import Panel

console = Console()

def _print_header():
    console.print(Panel.fit(
        "[bold cyan]PerfTrace CLI[/bold cyan] — Unified Performance Tracing",
        border_style="cyan"
    ))

@click.command()
@click.argument("function_name")
def show_function(function_name):
    """Show all trace records for a specific function in a single compact table."""
    _print_header()
    df = check_retrieve_data()
    filtered_df = df[df['function_name'] == function_name].copy()
    filtered_df.fillna('-', inplace=True)
    if filtered_df.empty:
        console.print(f"\n[red]No records found for function:[/red] [bold]{function_name}[/bold]")
        return
    get_compact_trace_table(filtered_df)

@click.command()
@click.argument("context_tag")
def show_context(context_tag):
    """Show all trace records for a specific context tag in a single compact table."""
    _print_header()
    df = check_retrieve_data()
    filtered_df = df[df['context_tag'] == context_tag].copy()
    filtered_df.fillna('-', inplace=True)
    if filtered_df.empty:
        console.print(f"\n[red]No records found for context:[/red] [bold]{context_tag}[/bold]")
        return
    get_compact_trace_table(filtered_df)
