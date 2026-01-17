import click
from rich.console import Console
from perftrace.storage.config_manager import ConfigManager

console = Console()


@click.command()
def create_config():
    """Interactive CLI to create or update the PerfTrace config."""
    config = ConfigManager.load_config()

    console.print("\n[bold yellow]PerfTrace Config Setup[/bold yellow]\n")

    db_name = click.prompt(
        "Database engine (duckdb/postgresql)",
        default=config["database"].get("engine", "duckdb"),
    ).lower()

    if db_name == "duckdb":
        config["database"]["engine"] = "duckdb"
        duckdb_path = click.prompt(
            "DuckDB file path",
            default=config["database"]["duckdb"].get("path", "./data/default.duckdb"),
        )
        config["database"]["duckdb"]["path"] = duckdb_path
        config["database"]["duckdb"]["read_only"] = click.confirm(
            "Read only mode?", default=False
        )

    elif db_name == "postgresql":
        config["database"]["engine"] = "postgresql"
        console.print("\n[bold blue]Enter PostgreSQL connection details[/bold blue]")
        pg = config["database"]["postgresql"]
        pg["host"] = click.prompt("Host", default=pg.get("host", "localhost"))
        pg["port"] = click.prompt("Port", default=pg.get("port", 5432), type=int)
        pg["user"] = click.prompt("Username", default=pg.get("user", "postgres"))
        pg["password"] = click.prompt("Password", default=pg.get("password", "changeme"), hide_input=True)

    else:
        console.print("[red]Invalid option. Choose 'duckdb' or 'postgresql'.[/red]")
        return

    ConfigManager.save_config(config)
    console.print(f"\n[green]Configuration saved successfully![/green]\n")


if __name__ == "__main__":
    create_config()
