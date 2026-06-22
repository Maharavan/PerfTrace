import click
from perftrace.cli.logger import get_recent_info_about_function_context
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
@click.argument("context_tag")
def recent_context(context_tag):
    """Show the most recent trace record for a context tag."""
    _print_header()
    df = check_retrieve_data()
    filtered_df = df[df['context_tag'] == context_tag].tail(1).copy()
    filtered_df.fillna('-', inplace=True)
    if filtered_df.empty:
        console.print(f"\n[red]No records found for context:[/red] [bold]{context_tag}[/bold]")
        return
    console.print(f"\n[bold yellow]Most recent record — Context:[/bold yellow] [green]{context_tag}[/green]")
    get_recent_info_about_function_context(filtered_df)

@click.command()
@click.argument("function_name")
def recent_function(function_name):
    """Show the most recent trace record for a function."""
    _print_header()
    df = check_retrieve_data()
    filtered_df = df[df['function_name'] == function_name].tail(1).copy()
    filtered_df.fillna('-', inplace=True)
    if filtered_df.empty:
        console.print(f"\n[red]No records found for function:[/red] [bold]{function_name}[/bold]")
        return
    console.print(f"\n[bold yellow]Most recent record — Function:[/bold yellow] [green]{function_name}[/green]")
    get_recent_info_about_function_context(filtered_df)
