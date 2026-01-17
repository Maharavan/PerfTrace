import click
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import find_slowest_fastest_executed
from rich import print

@click.command()
def slowest():
    """Show Top 10 slowest executed functions/Context Managers"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Recent Function data:[/bold yellow]")
    df.fillna('-')
    find_slowest_fastest_executed(df,'function_name',sort_by=False)
    print("\n[bold yellow]Recent Context Manager data:[/bold yellow]")
    find_slowest_fastest_executed(df,'context_tag',sort_by=False)