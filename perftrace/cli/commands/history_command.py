import click
from rich import print
from perftrace.cli.logger import filter_functions_context,formatize_function_context
from perftrace.cli.db_utils import check_retrieve_data
import datetime
import pandas as pd

@click.command
@click.option("--day")
def history(day):
    """Show PerfTrace today monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['timestamp']>=timestamp]
    
    print(f"\n[blue]History data function & Context calls for {day} days [/blue]")

    print("\n[bold yellow]Function name:[/bold yellow]")
    filter_functions_context(dataframe,'function_name')
    print("\n[bold yellow]Context Manager:[/bold yellow]")
    filter_functions_context(dataframe,'context_tag')

@click.command
@click.argument("function")
@click.option("--day",required=True,help="Specifies days to filter the function")
def search_function(function,day):
    """Show History PerfTrace  monitoring Function over specific days"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['timestamp']>=timestamp]
    dataframe = dataframe[dataframe['function_name']==function]
    formatize_function_context(dataframe)


@click.command
@click.argument("context")
@click.option("--day",required=True,help="Specifies days to filter the function")
def search_context(context,day):
    """Show History PerfTrace  monitoring Context manager over specific days"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['timestamp']>=timestamp]
    dataframe = dataframe[dataframe['context_tag']==context]
    formatize_function_context(dataframe)