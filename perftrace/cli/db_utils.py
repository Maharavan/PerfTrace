import click
from rich import print
from perftrace import __version__
from perftrace.storage.database_loader import DatabaseLoader
from perftrace.storage.config_manager import ConfigManager
DB_DATA = None

def check_retrieve_data():
    global DB_DATA
    config = ConfigManager.load_config()
    db_name = config.get('database',{}).get('engine','').lower()
    if db_name == 'duckdb':
        print("[yellow]Loading DuckDB database...[/yellow]")
        tablename = config['database'][db_name]['tablename']
        DB_DATA = DatabaseLoader.duckdb_database_pandas_converter(tablename)
    elif db_name == 'postgresql':
        print("[yellow]Loading Postgres database...[/yellow]")
        
        
    else:
        print("[green]Using cached database data[/green]")
    return DB_DATA

