import click
from perftrace import __version__
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

console = Console()

_GROUPS = [
    ("General", [
        "version", "help", "doctor", "summary", "list",
    ]),
    ("Function", [
        "show-function", "recent-function", "stats-function",
        "search-function", "count-function", "slowest", "fastest",
        "compare-function",
    ]),
    ("Context", [
        "show-context", "recent-context", "stats-context",
        "search-context", "count-context", "compare-context",
    ]),
    ("Time-based", [
        "today", "history",
    ]),
    ("System & Memory", [
        "system-status", "system-info", "system-monitor", "memory",
        "top-memory", "top-cpu",
    ]),
    ("Analysis", [
        "exceptions", "io-report",
    ]),
    ("Export — CSV", [
        "export-csv", "export-function-csv", "export-context-csv",
    ]),
    ("Export — JSON", [
        "export-json", "export-function-json", "export-context-json",
    ]),
    ("Export — HTML", [
        "export-html", "export-function-html", "export-context-html",
    ]),
    ("Database & Config", [
        "database-info", "set-config",
    ]),
]


@click.command()
def render_help():
    """Show PerfTrace help with grouped command reference."""
    from perftrace.cli.registry import cli_commands

    # ── Header ────────────────────────────────────────────────────────────────
    console.print(Panel.fit(
        f"[bold cyan]PerfTrace[/bold cyan]  [dim]v{__version__}[/dim]\n"
        "[dim]Unified performance tracing for Python — function, class, and context-level profiling[/dim]",
        border_style="cyan",
    ))

    # ── Quick start ───────────────────────────────────────────────────────────
    console.print("\n[bold yellow]Quick start[/bold yellow]")
    console.print("  [cyan]perftrace summary[/cyan]                   [dim]overview of all traces[/dim]")
    console.print("  [cyan]perftrace doctor[/cyan]                    [dim]verify config and DB[/dim]")
    console.print("  [cyan]perftrace stats-function[/cyan] [green]<name>[/green]      [dim]statistical breakdown[/dim]")
    console.print("  [cyan]perftrace show-function[/cyan]  [green]<name>[/green]      [dim]all runs in one table[/dim]")
    console.print("  [cyan]perftrace system-monitor[/cyan]            [dim]live CPU / RAM / disk[/dim]")
    console.print()

    # ── Command groups ────────────────────────────────────────────────────────
    for group_name, keys in _GROUPS:
        table = Table(
            title=f"[bold]{group_name}[/bold]",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            show_lines=False,
            padding=(0, 1),
            expand=False,
            title_justify="left",
        )
        table.add_column("Command",     style="cyan",       no_wrap=True, min_width=26)
        table.add_column("Description", style="white",      overflow="fold")

        for key in keys:
            entry = cli_commands.get(key)
            if entry is None:
                continue
            table.add_row(key, entry["description"])

        console.print(table)
        console.print()

    # ── Footer hint ───────────────────────────────────────────────────────────
    console.print(
        "[dim]Tip: run[/dim] [cyan]perftrace <command> --help[/cyan] "
        "[dim]for options on any individual command.[/dim]\n"
    )
