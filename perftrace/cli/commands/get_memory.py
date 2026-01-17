import click
from rich.console import Console
from rich.table import Table
from rich import print
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import inverted_print

@click.command
def memory():
    """Provides Memory used in Function/Context"""
    console = Console()
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    table = Table(title="Command List",style="yellow")
    table.add_column('Command',style='cyan')
    table.add_column('Description',style="green")
    df = check_retrieve_data()
    print("[bold yellow] Function data: [/bold yellow]")
    inverted_print(df,'function_name','memory_collector')
    print("[bold yellow] Context tag: [/bold yellow]")
    inverted_print(df,'context_tag','memory_collector')
