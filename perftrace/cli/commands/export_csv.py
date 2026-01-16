import click
from perftrace.cli.db_utils import check_retrieve_data
from rich import print
@click.command
@click.option('--filename',default='perftrace.csv',help='File name')
def export_result_csv(filename):
    df = check_retrieve_data()
    df.to_csv(filename)
    print(f'[green] Data stored in csv format: {filename}[/green]')
    

