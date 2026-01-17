import click
import uuid
from rich import print
from perftrace.cli.db_utils import check_retrieve_data

RANDOM_ID = uuid.uuid4()

def export_json(df, filename, limit=None, empty_msg="No data found"):
    """Shared JSON export utility"""

    if not filename.endswith(".json"):
        filename += ".json"

    if df.empty:
        print(f"[yellow]{empty_msg}[/yellow]")
        return

    if limit is not None:
        df = df.head(limit)

    df.to_json(filename, orient="records", indent=4)

    print(f"[bold green]Data successfully saved to {filename}[/bold green]")
    print(f"[cyan]Rows exported:[/cyan] {len(df)}")


@click.command(name="export-json")
@click.option(
    "--filename",
    default=f"perftrace_all_{RANDOM_ID}.json",
    help="Output JSON filename"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit number of rows"
)
def export_all_json(filename, limit):
    """Export complete PerfTrace database in JSON"""
    try:
        df = check_retrieve_data()
        export_json(df, filename, limit)

    except Exception as e:
        print(f"[bold red]Failed to export data:[/bold red] {e}")


@click.command(name="export-function-json")
@click.option(
    "--filename",
    default=f"perftrace_function_{RANDOM_ID}.json",
    help="Output JSON filename"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit number of rows"
)
def export_function_json(filename, limit):
    """Export Function-level data in JSON"""
    try:
        df = check_retrieve_data()

        df = df.dropna(subset=["context_tag"])

        export_json(
            df,
            filename,
            limit,
            empty_msg="No function data found"
        )

    except Exception as e:
        print(f"[bold red]Failed to export function data:[/bold red] {e}")


@click.command(name="export-context-json")
@click.option(
    "--filename",
    default=f"perftrace_context_{RANDOM_ID}.json",
    help="Output JSON filename"
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit number of rows"
)
def export_context_json(filename, limit):
    """Export Context Manager data in JSON"""
    try:
        df = check_retrieve_data()

        df = df.dropna(subset=["function_name"])

        export_json(
            df,
            filename,
            limit,
            empty_msg="No context data found"
        )

    except Exception as e:
        print(f"[bold red]Failed to export context data:[/bold red] {e}")
