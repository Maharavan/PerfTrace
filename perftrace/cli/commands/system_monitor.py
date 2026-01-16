import click
from perftrace.core.collectors import SystemCollector
from rich import print
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time
@click.command()
def system_monitor():
    """ Show Real system monitoring"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    print("\n[bold yellow]Stats System Stats data:[/bold yellow]")
    sys_data = SystemCollector().report()            
    console = Console()
    columns = [str(key) for key in sys_data.keys()]
    rows = []
    table = Table(title='System data')
    for col in columns:
        table.add_column(col, style='cyan')
    try:
        while True:
            with Live(table, screen=True, refresh_per_second=2) as live:
                sys_data = SystemCollector().report() 
                row = [str(value) for value in sys_data.values()]
                rows.insert(0, row)
                table = Table(title='System data')
                for col in columns:
                    table.add_column(col, style='cyan')
                for row in rows:
                    table.add_row(*row)
                live.update(table)
                time.sleep(5)
    except KeyboardInterrupt:
        console.print(table)
        print("\n[red]Monitoring stopped.[/red]")
