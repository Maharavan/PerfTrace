import platform
import click
from rich import print
from rich.console import Console
from rich.table import Table
@click.command()
def system_info():
    """Provides system information"""
    platform_data = platform.uname()

    system_details = {
        'System': platform_data.system,
        'Node Name': platform_data.node,
        'Release': platform_data.release,
        'Version': platform_data.version,
        'Machine': platform_data.machine,
        'Processor': platform_data.processor
    }

    console = Console()
    table = Table()
    table.add_column('Metrics',style='cyan')
    table.add_column('Result',style='magenta')

    for key,details in system_details.items():
        table.add_row(str(key),str(details))
    console.print(table)