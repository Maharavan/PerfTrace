import click
from rich import print
from perftrace.cli.logger import filter_functions_context,get_info_about_function_context
from perftrace.cli.db_utils import check_retrieve_data
import datetime
import pandas as pd

@click.command
@click.option("--day")
def history(day):
    """Show PerfTrace today monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['Timestamp']>=timestamp]
    
    print(f"\n[blue]History data function & Context calls for {day} days [/blue]")

    print("\n[bold yellow]Function name:[/bold yellow]")
    filter_functions_context(dataframe,'Function_name')
    print("\n[bold yellow]Context Manager:[/bold yellow]")
    filter_functions_context(dataframe,'Context_tag')

@click.command
@click.argument("function")
@click.option("--day",required=True,help="Specifies days to filter the function")
def search_function(function,day):
    """Show History PerfTrace  monitoring Function over specific days"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['Timestamp']>=timestamp]
    dataframe = dataframe[dataframe['Function_name']==function]
    get_info_about_function_context(dataframe)


@click.command
@click.argument("context")
@click.option("--day",required=True,help="Specifies days to filter the function")
def search_context(context,day):
    """Show History PerfTrace  monitoring Context manager over specific days"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    dataframe = check_retrieve_data()
    dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
    latest_timestamp = pd.Timestamp.now()
    timestamp = latest_timestamp - pd.Timedelta(days=int(day))
    dataframe = dataframe[dataframe['Timestamp']>=timestamp]
    dataframe = dataframe[dataframe['Context_tag']==context]
    get_info_about_function_context(dataframe)