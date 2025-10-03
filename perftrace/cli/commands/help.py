import click
from perftrace import __version__
from rich import print
from rich.console import Console
from rich.table import Table
@click.command()
def help():
    """Show PerfTrace help"""
    from perftrace.cli.registry import cli_commands
    console = Console()
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    print(f"[red]Version:[/red] [green]{__version__}[/green]")
    table = Table(title="Command List",style="yellow")
    table.add_column('Command',style='cyan')
    table.add_column('Description',style="green")
    for command,desc in cli_commands.items():
        table.add_row(command,desc['description'])
    
    console.print(table)
    
