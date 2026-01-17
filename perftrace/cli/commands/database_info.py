import click
import duckdb
import psycopg2
from rich import print
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.storage.config_manager import ConfigManager
from perftrace.storage import DB_TABLE_NAME
from psycopg2 import sql
@click.command
def database_info():
    """Provides Database information"""
    config = ConfigManager.load_config()
    print("[bold cyan] Database Information [/bold cyan]")
    get_database = config.get("database").get("engine")
    if get_database.lower() == 'duckdb':
        db_path = config.get("database").get("duckdb").get("path")
        with duckdb.connect(database=db_path) as con:
            con.execute(f"SELECT COUNT(*) FROM {DB_TABLE_NAME}")
            record = con.fetchone()[0]
        print("[green] Database: [/green]",get_database)
        print("[yellow] Version: [/yellow]",duckdb.__version__)
        print("[yellow] Path : [/yellow]",db_path)
        print("[yellow] Record count : [/yellow]",record)

        
    elif get_database.lower() == 'postgresql':
        conn = psycopg2.connect(
            user=config.get("database").get("postgresql").get("user"),
            host = config.get("database").get("postgresql").get("host"),
            port = config.get("database").get("postgresql").get("port"),
            password = config.get("database").get("postgresql").get("password")
        )
        with conn.cursor() as cur:
            cur.execute("SHOW server_version;")
            version = cur.fetchone()[0]
            sql_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(DB_TABLE_NAME))
            cur.execute(sql_query)
            record = cur.fetchone()[0]

        print("[green] Database: [/green]",get_database)
        print("[yellow] Host : [/yellow]",config.get("database").get("postgresql").get("host"))
        print("[yellow] Port : [/yellow]",config.get("database").get("postgresql").get("port"))
        print("[yellow] user : [/yellow]",config.get("database").get("postgresql").get("user"))
        print("[yellow] Version : [/yellow]",version)
        print("[yellow] Record count : [/yellow]",record)
