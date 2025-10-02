import click
from rich import print
from perftrace import __version__
from perftrace.storage.database_loader import database_pandas_converter
from perftrace.cli.logger import filter_functions_context
from perftrace.cli.logger import get_info_about_function_context
from perftrace.cli.logger import statistical_summary
from perftrace.cli.logger import find_slowest_fastest_executed

DB_DATA = None

def check_retrieve_data():
    if DB_DATA:
        return DB_DATA
    return database_pandas_converter()

@click.command()
def version():
    """Show PerfTrace version"""
    print(f"[red]PerfTrace :[/red] [green]{__version__}[/green]")


@click.command()
def help():
    """Show PerfTrace help"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    print(f"[red]Version:[/red] [green]{__version__}[/green]")
    print("\n[bold yellow]Commands:[/bold yellow]")
    


@click.command()
def list():
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Function name:[/bold yellow]")
    filter_functions_context(df,'Function_name')
    print("\n[bold yellow]Context Manager:[/bold yellow]")

    filter_functions_context(df,'Context_tag')

@click.command()
@click.argument("function_name")
def show_function(function_name):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['Function_name']==function_name]
    filtered_df.fillna('-')
    get_info_about_function_context(filtered_df)

@click.command()
@click.argument("context_tag")
def show_context(context_tag):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['Context_tag']==context_tag]
    filtered_df.fillna('-')
    get_info_about_function_context(filtered_df)

@click.command()
@click.argument("context_tag")
def recent_context(context_tag):
    """Show Latest PerfTrace monitoring function data"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow] Recent Function data:[/bold yellow]")
    filtered_df = df[df['Context_tag']==context_tag].tail(1)
    filtered_df.fillna('-')
    get_info_about_function_context(filtered_df)

@click.command()
@click.argument("function_name")
def recent_function(function_name):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Recent Function data:[/bold yellow]")
    filtered_df = df[df['Function_name']==function_name].tail(1)
    filtered_df.fillna('-')
    get_info_about_function_context(filtered_df)


@click.command()
@click.argument("context_tag")
def stats_context(context_tag):
    """Show Statistical PerfTrace monitoring Context Manager"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow] Stats Context data:[/bold yellow]")
    filtered_df = df[df['Context_tag']==context_tag]
    filtered_df.fillna('-')
    statistical_summary(filtered_df)

@click.command()
@click.argument("function_name")
def stats_function(function_name):
    """Show Statistical PerfTrace monitoring function"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Stats Function data:[/bold yellow]")
    filtered_df = df[df['Function_name']==function_name]
    filtered_df.fillna('-')
    statistical_summary(filtered_df)

@click.command()
def slowest():
    """Show slowest executed functions/Context Managers"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Recent Function data:[/bold yellow]")
    df.fillna('-')
    find_slowest_fastest_executed(df,'Function_name',False)
    print("\n[bold yellow]Recent Context Manager data:[/bold yellow]")
    find_slowest_fastest_executed(df,'Context_tag',False)


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