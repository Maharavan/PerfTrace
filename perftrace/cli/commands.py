import click
from rich import print
from perftrace import __version__
from perftrace.storage.database_loader import database_pandas_converter
from perftrace.cli.helper import filter_functions_context,get_info_about_function_context
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
    print("  [green]version[/green]   Show PerfTrace version")
    print("  [green]help[/green]      Show this help message")

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
def show(function_name):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Function data:[/bold yellow]")
    get_info_about_function_context(df,function_name)