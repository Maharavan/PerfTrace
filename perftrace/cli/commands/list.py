import click
from rich import print
from perftrace.cli.logger import filter_functions_context
from perftrace.cli.db_utils import check_retrieve_data

@click.command()
def list():
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Function name:[/bold yellow]")
    filter_functions_context(df,'Function_name')
    print("\n[bold yellow]Context Manager:[/bold yellow]")

    filter_functions_context(df,'Context_tag')
