import click
from rich import print
from perftrace.cli.command_utils import check_retrieve_data
from perftrace.cli.logger import find_slowest_fastest_executed
@click.command()
def fastest():
    """Show Fastest executed functions/Context Managers"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Function data:[/bold yellow]")
    df.fillna('-')
    find_slowest_fastest_executed(df,'Function_name',True)
    print("\n[bold yellow]Context Manager data:[/bold yellow]")
    find_slowest_fastest_executed(df,'Context_tag',True)