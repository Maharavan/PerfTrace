import click
from rich import print
from perftrace import __version__
from perftrace.storage.database_loader import DatabaseLoader
from perftrace.storage.config_manager import ConfigManager
from perftrace.storage import DB_TABLE_NAME
DB_DATA = None

def check_retrieve_data():
    global DB_DATA
    config = ConfigManager.load_config()
    db_name = config.get('database',{}).get('engine','').lower()
    if db_name == 'duckdb':
        print("[yellow]Loading DuckDB database...[/yellow]")
        DB_DATA = DatabaseLoader.duckdb_database_pandas_converter(DB_TABLE_NAME)
    elif db_name == 'postgresql':
        print("[yellow]Loading Postgresql database...[/yellow]")
        DB_DATA = DatabaseLoader.postgresql_database_pandas_converter(DB_TABLE_NAME)
    return DB_DATA

