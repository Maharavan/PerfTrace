import click
from perftrace.cli.command_utils import check_retrieve_data
from perftrace.cli.logger import statistical_summary
from rich import print

@click.command()
@click.argument("context_tag")
def stats_context(context_tag):
    """Show Statistical PerfTrace monitoring Context Manager"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow] Stats Context data:[/bold yellow]")
    filtered_df = df[df['Context_tag']==context_tag]
    filtered_df.fillna('-',inplace=True)
    statistical_summary(filtered_df)

@click.command()
@click.argument("function_name")
def stats_function(function_name):
    """Show Statistical PerfTrace monitoring function"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    df = check_retrieve_data()
    print("\n[bold yellow]Stats Function data:[/bold yellow]")
    filtered_df = df[df['Function_name']==function_name]
    filtered_df.fillna('-',inplace=True)
    statistical_summary(filtered_df)
