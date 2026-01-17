import click
from rich import print
from perftrace.cli.logger import filter_functions_context
from perftrace.cli.db_utils import check_retrieve_data
import datetime
import pandas as pd
@click.command
def today():
    """Show PerfTrace today monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    today = datetime.datetime.now().date()
    dataframe = dataframe[dataframe['timestamp'].dt.date==today]
    print("\n[blue]Today Function & Context calls [/blue]")

    print("\n[bold yellow]Function name:[/bold yellow]")
    filter_functions_context(dataframe,'function_name')
    print("\n[bold yellow]Context Manager:[/bold yellow]")
    filter_functions_context(dataframe,'context_tag')
