import click
from perftrace.core.collectors import SystemCollector
from rich import print
from rich.table import Table
from rich.console import Console

@click.command()
def system_data():
    """Show Statistical PerfTrace monitoring Context Manager"""
    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")
    sys_data = SystemCollector().report()
    print("\n[bold yellow] Stats System Stats data:[/bold yellow]")
    
    table = Table(title='System data')
    console = Console()
    table.add_column('Metric',style='cyan')
    table.add_column('Result',style='magenta')

    for key,data in sys_data.items():
        table.add_row(str(key),str(data))
    console.print(table)