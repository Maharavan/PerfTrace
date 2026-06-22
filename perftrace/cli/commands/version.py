import platform
import click
from rich.console import Console
from rich.panel import Panel
from perftrace import __version__

console = Console()


@click.command()
def version():
    """Show PerfTrace version and runtime details."""
    console.print(Panel.fit(
        f"[bold cyan]PerfTrace[/bold cyan]  [bold green]{__version__}[/bold green]\n"
        f"[dim]Python {platform.python_version()}  ·  {platform.system()} {platform.release()}[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))
