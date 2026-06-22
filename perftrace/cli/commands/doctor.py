import click
import os
import shutil
import platform
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from perftrace.storage.config_manager import ConfigManager
from perftrace.cli.db_utils import check_retrieve_data

console = Console()


def _check_row(table, label, ok, detail, warn=False):
    if ok:
        icon = "[bold green]✔[/bold green]"
        style = "green"
    elif warn:
        icon = "[bold yellow]⚠[/bold yellow]"
        style = "yellow"
    else:
        icon = "[bold red]✖[/bold red]"
        style = "red"
    table.add_row(icon, f"[{style}]{label}[/{style}]", detail)


@click.command()
def doctor():
    """Run health checks for PerfTrace and report overall status."""
    console.print(Panel.fit(
        "[bold cyan]PerfTrace Doctor[/bold cyan]  [dim]Health Check[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    t = Table(
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        border_style="dim cyan",
        padding=(0, 1),
        expand=True,
    )
    t.add_column("",       width=3,    no_wrap=True)
    t.add_column("Check",  style="white", no_wrap=True, min_width=26)
    t.add_column("Detail", style="dim",   overflow="fold")

    issues = 0

    # Config
    try:
        config = ConfigManager.load_config()
        _check_row(t, "Config file loaded", True, str(ConfigManager._config_path()))
    except Exception as e:
        _check_row(t, "Config file loaded", False, str(e))
        issues += 1

    # Database
    try:
        df = check_retrieve_data()
        _check_row(t, "Database connectivity", True,
                   f"{len(df):,} record{'s' if len(df) != 1 else ''} found")
    except Exception as e:
        _check_row(t, "Database connectivity", False, str(e))
        issues += 1

    # Disk space
    _, _, free = shutil.disk_usage(os.getcwd())
    free_gb = free / (1024 ** 3)
    if free_gb < 1:
        _check_row(t, "Disk space", False,
                   f"{free_gb:.1f} GB free — critically low", warn=False)
        issues += 1
    elif free_gb < 2:
        _check_row(t, "Disk space", False,
                   f"{free_gb:.1f} GB free — low", warn=True)
    else:
        _check_row(t, "Disk space", True, f"{free_gb:.1f} GB free")

    # Python version
    py_ver = platform.python_version_tuple()
    py_ok  = int(py_ver[0]) >= 3 and int(py_ver[1]) >= 11
    _check_row(t, "Python version ≥ 3.11", py_ok,
               platform.python_version(),
               warn=not py_ok)
    if not py_ok:
        issues += 1

    # OS
    _check_row(t, "Operating system", True,
               f"{platform.system()} {platform.release()}")

    console.print(t)

    if issues == 0:
        verdict_color, verdict_text, border = "green", "HEALTHY", "green"
    elif issues <= 1:
        verdict_color, verdict_text, border = "yellow", "DEGRADED", "yellow"
    else:
        verdict_color, verdict_text, border = "red", "UNHEALTHY", "red"

    console.print(Panel.fit(
        f"[bold {verdict_color}]Overall Status: {verdict_text}[/bold {verdict_color}]"
        + (f"  [dim]({issues} issue{'s' if issues != 1 else ''})[/dim]" if issues else ""),
        border_style=border,
        padding=(0, 2),
    ))
