import csv
import json
import os
import uuid
import pandas as pd
import click
from rich.console import Console
from rich.panel import Panel
from perftrace.cli.db_utils import check_retrieve_data

console = Console()
RANDOM_ID = uuid.uuid4()


def flatten_value(value, parent_key="", sep="."):
    items = {}

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return {parent_key: value}

    if isinstance(value, dict):
        for k, v in value.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_value(v, new_key, sep))

    elif isinstance(value, list):
        for i, v in enumerate(value):
            new_key = f"{parent_key}{sep}{i}"
            items.update(flatten_value(v, new_key, sep))

    else:
        items[parent_key] = value

    return items


def auto_flatten_dataframe(df, sep="."):
    rows = []
    for _, row in df.iterrows():
        flat_row = {}
        for col, value in row.items():
            flat_row.update(flatten_value(value, col, sep))
        rows.append(flat_row)
    df_flat = pd.DataFrame(rows)
    df_flat = df_flat.dropna(axis=1, how="all")
    return df_flat


def _export_csv(df, filename, label):
    if not filename.endswith(".csv"):
        filename += ".csv"

    if df.empty:
        console.print(f"[yellow]No {label} data found to export.[/yellow]")
        return

    df_flat = auto_flatten_dataframe(df)
    df_flat.to_csv(filename, index=False, quoting=csv.QUOTE_ALL)

    abs_path = os.path.abspath(filename)
    size_kb = os.path.getsize(abs_path) / 1024
    console.print(Panel.fit(
        f"[bold green]CSV export successful[/bold green]\n"
        f"[cyan]File:[/cyan]  {abs_path}\n"
        f"[cyan]Rows:[/cyan]  {len(df_flat)}\n"
        f"[cyan]Size:[/cyan]  {size_kb:.1f} KB",
        title=f"[bold]{label} Export[/bold]",
        border_style="green"
    ))


@click.command()
@click.option('--filename', default=f'perftrace_all_{RANDOM_ID}.csv', help="Output CSV filename")
def export_result_csv(filename):
    """Export complete PerfTrace database to CSV."""
    df = check_retrieve_data()
    _export_csv(df, filename, "All Data")


@click.command()
@click.option('--filename', default=f'perftrace_function_{RANDOM_ID}.csv', help="Output CSV filename")
def export_function_csv(filename):
    """Export function trace records to CSV."""
    df = check_retrieve_data()
    if "function_name" in df.columns:
        df = df.dropna(subset=["function_name"])
    if "context_tag" in df.columns:
        df = df.drop(columns=["context_tag"])
    _export_csv(df, filename, "Function")


@click.command()
@click.option('--filename', default=f'perftrace_context_{RANDOM_ID}.csv', help="Output CSV filename")
def export_context_csv(filename):
    """Export context manager trace records to CSV."""
    df = check_retrieve_data()
    if "context_tag" in df.columns:
        df = df.dropna(subset=["context_tag"])
    if "function_name" in df.columns:
        df = df.drop(columns=["function_name"])
    _export_csv(df, filename, "Context")
