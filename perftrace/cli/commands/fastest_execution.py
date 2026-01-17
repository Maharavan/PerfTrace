import click
from rich import print
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import find_slowest_fastest_executed
@click.command()
def fastest():
    """Show Top 10 Fastest executed functions/Context Managers"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Function data:[/bold yellow]")
    if df is None or df.empty:
        print("\n[bold red]Dataframe empty [/bold red]")
        return
    df.fillna('-')
    find_slowest_fastest_executed(df,'function_name',sort_by=True)
    print("\n[bold yellow]Context Manager data:[/bold yellow]")
    find_slowest_fastest_executed(df,'context_tag',sort_by=True)