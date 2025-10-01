import click
from rich import print
from perftrace import __version__

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
