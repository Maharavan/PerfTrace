import click
import os
import shutil
import platform
from rich import print
from perftrace.storage.config_manager import ConfigManager
from perftrace.cli.db_utils import check_retrieve_data


@click.command()
def doctor():
    """Run health checks for PerfTrace"""

    print("[bold cyan]PerfTrace Doctor[/bold cyan]")
    print("────────────────────────────────────────")

    # Config check
    try:
        config = ConfigManager.load_config()
        print("[green]✔ Config file loaded[/green]")
    except Exception as e:
        print(f"[red]✖ Config error:[/red] {e}")
        return

    try:
        df = check_retrieve_data()
        print("[green]✔ Database connectivity[/green]")
        print(f"    Records found : {len(df)}")
    except Exception as e:
        print(f"[red]✖ Database error:[/red] {e}")
        return

    _, _, free = shutil.disk_usage(os.getcwd())
    free_gb = free // (1024 ** 3)

    if free_gb < 2:
        print(f"[yellow]⚠ Low disk space:[/yellow] {free_gb} GB free")
    else:
        print(f"[green]✔ Disk space OK:[/green] {free_gb} GB free")

    print("[green]✔ Environment[/green]")
    print(f"    OS     : {platform.system()}")
    print(f"    Python : {platform.python_version()}")

    print("\n[bold green]Overall Status: HEALTHY[/bold green]")
