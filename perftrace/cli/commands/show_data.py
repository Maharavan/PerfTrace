import click
from perftrace.cli.logger import get_info_about_function_context
from perftrace.cli.command_utils import check_retrieve_data
from rich import print

@click.command()
@click.argument("function_name")
def show_function(function_name):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['Function_name']==function_name]
    filtered_df.fillna('-',inplace=True)
    get_info_about_function_context(filtered_df)

@click.command()
@click.argument("context_tag")
def show_context(context_tag):
    """Show PerfTrace monitoring functions"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Overall Function data:[/bold yellow]")
    filtered_df = df[df['Context_tag']==context_tag]
    filtered_df.fillna('-',inplace=True)
    get_info_about_function_context(filtered_df)

