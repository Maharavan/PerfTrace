import click
from perftrace import __version__
from rich import print

@click.command()
def version():
    """Show PerfTrace version"""
    print(f"[red]PerfTrace :[/red] [green]{__version__}[/green]")

