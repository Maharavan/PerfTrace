import click
import duckdb
import psycopg2
from psycopg2 import sql
from rich import print
from perftrace.storage.config_manager import ConfigManager
from perftrace.storage import DB_TABLE_NAME


@click.command()
def database_info():
    """Provides Database information"""
    config = ConfigManager.load_config()
    db_config = config.get("database", {})
    engine = db_config.get("engine", "").lower()

    print("[bold cyan]Database Information[/bold cyan]")

    try:
        if engine == "duckdb":
            _duckdb_info(db_config)

        elif engine == "postgresql":
            _postgres_info(db_config)

        else:
            print("[red]Unsupported database engine[/red]")

    except Exception as e:
        print(f"[red]Error:[/red] {e}")


def _duckdb_info(db_config):
    db_path = db_config["duckdb"]["path"]

    with duckdb.connect(database=db_path) as con:
        record = con.execute(
            f"SELECT COUNT(*) FROM {DB_TABLE_NAME}"
        ).fetchone()[0]

    print("[green]Database:[/green] DuckDB")
    print("[yellow]Version:[/yellow]", duckdb.__version__)
    print("[yellow]Path:[/yellow]", db_path)
    print("[yellow]Record count:[/yellow]", record)


def _postgres_info(db_config):
    pg = db_config["postgresql"]

    with psycopg2.connect(
        dbname=pg["database"],
        user=pg["user"],
        host=pg["host"],
        port=pg["port"],
        password=pg["password"]
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW server_version;")
            version = cur.fetchone()[0]

            cur.execute(
                sql.SQL("SELECT COUNT(*) FROM {}")
                .format(sql.Identifier(DB_TABLE_NAME))
            )
            record = cur.fetchone()[0]

    print("[green]Database:[/green] PostgreSQL")
    print("[yellow]Host:[/yellow]", pg["host"])
    print("[yellow]Port:[/yellow]", pg["port"])
    print("[yellow]User:[/yellow]", pg["user"])
    print("[yellow]Version:[/yellow]", version)
    print("[yellow]Record count:[/yellow]", record)
