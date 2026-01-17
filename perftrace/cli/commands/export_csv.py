import click
import csv
import json
import uuid
import pandas as pd
from rich import print
from perftrace.cli.db_utils import check_retrieve_data

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

@click.command
@click.option('--filename', default=f'perftrace_final_{RANDOM_ID}.csv')
def export_result_csv(filename):
    """Export Database result in CSV format"""
    df = check_retrieve_data()
    df_flat = auto_flatten_dataframe(df)

    df_flat.to_csv(
        filename,
        index=False,
        quoting=csv.QUOTE_ALL
    )

    print(f'[green]Auto-flattened CSV exported: {filename}[/green]')


@click.command
@click.option('--filename', default=f'perftrace_function_{RANDOM_ID}.csv')
def export_function_csv(filename):
    """Export Function result in CSV format"""

    df = check_retrieve_data()
    df_flat = auto_flatten_dataframe(df)

    if "context_tag" in df_flat.columns:
        df_flat = df_flat.drop(columns=["context_tag"])

    if "function_name" in df_flat.columns:
        df_flat = df_flat.dropna(subset=["function_name"])

    df_flat.to_csv(
        filename,
        index=False,
        quoting=csv.QUOTE_ALL
    )

    print(f'[green]Flattened function CSV exported: {filename}[/green]')


@click.command
@click.option('--filename', default=f'perftrace_context_tag_{RANDOM_ID}.csv')
def export_context_csv(filename):
    """Export Context Manager result in CSV format"""

    df = check_retrieve_data()
    df_flat = auto_flatten_dataframe(df)

    if "function_name" in df_flat.columns:
        df_flat = df_flat.drop(columns=["function_name"])

    if "context_tag" in df_flat.columns:
        df_flat = df_flat.dropna(subset=["context_tag"])

    df_flat.to_csv(
        filename,
        index=False,
        quoting=csv.QUOTE_ALL
    )

    print(f'[green]Flattened context CSV exported: {filename}[/green]')
