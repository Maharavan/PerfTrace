import click
from perftrace.cli.logger import get_recent_info_about_function_context
from perftrace.cli.db_utils import check_retrieve_data
from rich import print

@click.command()
@click.argument("function_name")
def show_function(function_name):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['function_name']==function_name]
    filtered_df.fillna('-',inplace=True)
    get_recent_info_about_function_context(filtered_df)

@click.command()
@click.argument("context_tag")
def show_context(context_tag):
    """Show PerfTrace monitoring Context Manager"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['context_tag']==context_tag]
    filtered_df.fillna('-',inplace=True)
    get_recent_info_about_function_context(filtered_df)

