import click
import csv
import json
import uuid
import pandas as pd
from rich import print
from perftrace.cli.db_utils import check_retrieve_data

random_id = uuid.uuid4()

@click.command
@click.option('--filename', default=f'perftrace_final_{random_id}.json')
def export_result_json(filename):
    """Export Database result in JSON"""

    df = check_retrieve_data()
    df.to_json(filename,indent=4)
    print(f"[bold green] DataFrame successfully saved to {filename} [/bold green]")



