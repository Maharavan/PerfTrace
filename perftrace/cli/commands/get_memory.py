import click
from rich.console import Console
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.cli.logger import inverted_print

@click.command
def memory():
    console = Console()
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    table = Table(title="Command List",style="yellow")
    table.add_column('Command',style='cyan')
    table.add_column('Description',style="green")
    df = check_retrieve_data()
    inverted_print(df,'Function_name','MemoryCollector')
    inverted_print(df,'Context_tag','MemoryCollector')
