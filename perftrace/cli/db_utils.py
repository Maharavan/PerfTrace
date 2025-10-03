import click
from rich import print
from perftrace import __version__
from perftrace.storage.database_loader import database_pandas_converter

DB_DATA = None

def check_retrieve_data():
    global DB_DATA
    if DB_DATA is None:
        print("[yellow]Loading database...[/yellow]")
        DB_DATA = database_pandas_converter()
    else:
        print("[green]Using cached database data[/green]")
    return DB_DATA

