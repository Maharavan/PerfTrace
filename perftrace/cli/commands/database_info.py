import click
import duckdb
import psycopg2
from rich import print
from perftrace.cli.db_utils import check_retrieve_data
from perftrace.storage.config_manager import ConfigManager

@click.command
def database_info():
    """Provides Database information"""
    config = ConfigManager.load_config()
    print("[bold cyan] Database Information [/bold cyan]")
    get_database = config.get("database").get("engine")
    if get_database.lower() == 'duckdb':
        print("[green] Database: [/green]",get_database)
        print("[yellow] Version: [/yellow]",duckdb.__version__)
        print("[yellow] Path : [/yellow]",config.get("database").get("duckdb").get("path"))
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
        print("[green] Database: [/green]",get_database)
        print("[yellow] Host : [/yellow]",config.get("database").get("postgresql").get("host"))
        print("[yellow] Port : [/yellow]",config.get("database").get("postgresql").get("port"))
        print("[yellow] user : [/yellow]",config.get("database").get("postgresql").get("user"))
        print("[yellow] Version : [/yellow]",version)
