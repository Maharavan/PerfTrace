import platform
import sys
import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from perftrace import __version__ as perftrace_version

console = Console()


@click.command()
def system_info():
    """Show platform, Python, and PerfTrace environment details."""
    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]System Information[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    uname = platform.uname()

    # ── Platform section ──────────────────────────────────────────────────────
    t_plat = Table(
        title="[bold cyan]Platform[/bold cyan]",
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        border_style="dim cyan",
        padding=(0, 1),
        expand=True,
    )
    t_plat.add_column("Field",  style="cyan",  no_wrap=True, min_width=20)
    t_plat.add_column("Value",  style="white", overflow="fold")

    t_plat.add_row("OS",          f"{uname.system} {uname.release}")
    t_plat.add_row("OS Version",  uname.version[:80] if uname.version else "-")
    t_plat.add_row("Host Name",   uname.node)
    t_plat.add_row("Architecture", uname.machine)
    t_plat.add_row("Processor",   uname.processor or platform.processor() or "-")
    console.print(t_plat)

    # ── Python section ─────────────────────────────────────────────────────────
    t_py = Table(
        title="[bold blue]Python Runtime[/bold blue]",
        show_header=True,
        header_style="bold blue",
        show_lines=False,
        border_style="dim blue",
        padding=(0, 1),
        expand=True,
    )
    t_py.add_column("Field",  style="cyan",  no_wrap=True, min_width=20)
    t_py.add_column("Value",  style="white", overflow="fold")

    t_py.add_row("Python Version",    platform.python_version())
    t_py.add_row("Python Build",      " ".join(platform.python_build()))
    t_py.add_row("Python Compiler",   platform.python_compiler())
    t_py.add_row("Python Executable", sys.executable)
    t_py.add_row("Python Path",       os.path.dirname(sys.executable))
    console.print(t_py)

    # ── PerfTrace section ──────────────────────────────────────────────────────
    t_pt = Table(
        title="[bold green]PerfTrace Environment[/bold green]",
        show_header=True,
        header_style="bold green",
        show_lines=False,
        border_style="dim green",
        padding=(0, 1),
        expand=True,
    )
    t_pt.add_column("Field",  style="cyan",  no_wrap=True, min_width=20)
    t_pt.add_column("Value",  style="white", overflow="fold")

    t_pt.add_row("PerfTrace Version", f"[bold cyan]{perftrace_version}[/bold cyan]")
    t_pt.add_row("Platform Tag",      platform.platform())
    console.print(t_pt)
