import click
from rich.console import Console
from rich.panel import Panel
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import find_slowest_fastest_executed

console = Console()


@click.command()
def fastest():
    """Show the 10 fastest executed functions and context managers."""
    df = check_retrieve_data()
    if df is None or df.empty:
        console.print(Panel("[yellow]No trace data found.[/yellow]", border_style="yellow"))
        return
    df = df.fillna("-")
    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]Top 10 Fastest Executions[/dim]",
        border_style="cyan", padding=(0, 2),
    ))
    find_slowest_fastest_executed(df, "function_name", sort_by=True)
    find_slowest_fastest_executed(df, "context_tag",   sort_by=True)
