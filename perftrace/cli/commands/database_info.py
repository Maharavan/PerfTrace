import click
import duckdb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from perftrace.storage.config_manager import ConfigManager
from perftrace.storage import DB_TABLE_NAME

console = Console()


def _info_table(title, color="cyan"):
    t = Table(
        title=f"[bold {color}]{title}[/bold {color}]",
        show_header=True,
        header_style=f"bold {color}",
        show_lines=False,
        border_style=f"dim {color}",
        padding=(0, 1),
        expand=True,
    )
    t.add_column("Field",  style="cyan",  no_wrap=True, min_width=20)
    t.add_column("Value",  style="white", overflow="fold")
    return t


@click.command()
def database_info():
    """Show active database engine, connection details, and record count."""
    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]Database Information[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    try:
        config = ConfigManager.load_config()
    except Exception as e:
        console.print(f"[bold red]Config error:[/bold red] {e}")
        return

    db_config = config.get("database", {})
    engine    = db_config.get("engine", "").lower()

    try:
        if engine == "duckdb":
            _duckdb_info(db_config)
        elif engine == "postgresql":
            _postgres_info(db_config)
        else:
            console.print(f"[red]Unsupported database engine:[/red] [white]{engine or '(none)'}[/white]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


def _duckdb_info(db_config):
    import os
    db_path = db_config.get("duckdb", {}).get("path", "-")

    record_count = "-"
    table_cols   = "-"
    db_size      = "-"
    try:
        with duckdb.connect(database=db_path, read_only=True) as con:
            record_count = con.execute(
                f"SELECT COUNT(*) FROM {DB_TABLE_NAME}"
            ).fetchone()[0]
            cols = con.execute(
                f"PRAGMA table_info('{DB_TABLE_NAME}')"
            ).fetchall()
            table_cols = str(len(cols))
        if os.path.exists(db_path):
            size_bytes = os.path.getsize(db_path)
            if size_bytes < 1024 ** 2:
                db_size = f"{size_bytes / 1024:.1f} KB"
            else:
                db_size = f"{size_bytes / 1024 ** 2:.2f} MB"
    except Exception as e:
        record_count = f"[red]{e}[/red]"

    t = _info_table("DuckDB", "cyan")
    t.add_row("Engine",       "[bold cyan]DuckDB[/bold cyan]")
    t.add_row("Version",      duckdb.__version__)
    t.add_row("File Path",    db_path)
    t.add_row("File Size",    db_size)
    t.add_section()
    t.add_row("Table",        DB_TABLE_NAME)
    t.add_row("Columns",      table_cols)
    t.add_row("Record Count", f"[bold green]{record_count:,}[/bold green]"
              if isinstance(record_count, int) else str(record_count))
    console.print(t)


def _postgres_info(db_config):
    import psycopg2
    from psycopg2 import sql as pgsql

    pg = db_config.get("postgresql", {})

    version      = "-"
    record_count = "-"
    table_cols   = "-"
    db_size      = "-"
    try:
        with psycopg2.connect(
            dbname=pg["database"],
            user=pg["user"],
            host=pg["host"],
            port=pg["port"],
            password=pg["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW server_version;")
                version = cur.fetchone()[0]

                cur.execute(
                    pgsql.SQL("SELECT COUNT(*) FROM {}")
                    .format(pgsql.Identifier(DB_TABLE_NAME))
                )
                record_count = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM information_schema.columns "
                    "WHERE table_name = %s",
                    (DB_TABLE_NAME,)
                )
                table_cols = cur.fetchone()[0]

                cur.execute(
                    pgsql.SQL("SELECT pg_size_pretty(pg_total_relation_size({}))")
                    .format(pgsql.Literal(DB_TABLE_NAME))
                )
                db_size = cur.fetchone()[0]
    except Exception as e:
        record_count = f"[red]{e}[/red]"

    t = _info_table("PostgreSQL", "blue")
    t.add_row("Engine",   "[bold blue]PostgreSQL[/bold blue]")
    t.add_row("Version",  version)
    t.add_row("Host",     pg.get("host", "-"))
    t.add_row("Port",     str(pg.get("port", "-")))
    t.add_row("User",     pg.get("user", "-"))
    t.add_row("Database", pg.get("database", "-"))
    t.add_section()
    t.add_row("Table",        DB_TABLE_NAME)
    t.add_row("Columns",      str(table_cols))
    t.add_row("Table Size",   db_size)
    t.add_row("Record Count", f"[bold green]{record_count:,}[/bold green]"
              if isinstance(record_count, int) else str(record_count))
    console.print(t)
