from collections import defaultdict
import json
import pandas as pd
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

def filter_functions_context(df,column_value):
    remove_duplicates = set()
    for function_name in df[column_value]:
        if function_name not in remove_duplicates and function_name is not None:
            print(f"[green]{function_name}[/green]")
        if function_name is not None:
            remove_duplicates.add(function_name)
    if not remove_duplicates:
        print(f"[red]No info available[/red]")


def get_info_about_function_context(dataframe):
    """Display detailed information about each Function or Context."""
    if dataframe.empty:
        console.print("[red]Empty result. Please provide valid command.[/red]")
        return

    for idx, row in dataframe.iterrows():
        func_name = row.get("Function_name", "N/A")
        ctx_tag = row.get("Context_tag", "N/A")
        timestamp = row.get("Timestamp", "N/A")
        tit_header = func_name if func_name != "N/A" else ctx_tag
        table = Table(title=f"Function/Context Report — {tit_header}")
        table.add_column("Metrics", style="cyan", no_wrap=True)
        table.add_column("Values", style="magenta", overflow="fold")

        if func_name is not None:
            table.add_row("Function Name", str(func_name))
        if ctx_tag is not None:
            table.add_row("Context Tag", str(ctx_tag)) 
        table.add_row("Timestamp", str(timestamp))
        table.add_section()

        for metric, results in row.items():
            if metric in ("Timestamp", "Function_name", "Context_tag"):
                continue
            if results in (None, "-", ""):
                continue
            try:
                parsed = json.loads(results)
                if isinstance(parsed, dict):
                    formatted = "\n".join([f"{k}: {v}" for k, v in parsed.items()])
                    table.add_row(metric, formatted)
                else:
                    table.add_row(metric, str(parsed))
            except Exception:
                table.add_row(metric, str(results))

        console.print(table)



def statistical_summary(dataframe):
    """Generate statistical summary (min, max, avg) for JSON metrics."""
    if dataframe.empty:
        console.print("[red]Empty result. Please provide valid command.[/red]")
        return

    dataframe_modified = dataframe.drop(
        ['Timestamp', 'Function_name', 'Context_tag'], axis=1, errors="ignore"
    )
    max_collector = defaultdict(lambda: float('-inf'))
    min_collector = defaultdict(lambda: float('inf'))
    avg_collector = defaultdict(list)

    for col in dataframe_modified.columns:
        for val in dataframe_modified[col]:
            if val in (None, '-', ''):
                continue
            try:
                val_dict = json.loads(val)
                if not isinstance(val_dict, dict):
                    continue
            except Exception:
                continue

            for key, data in val_dict.items():
                if isinstance(data, (int, float)):
                    max_collector[key] = max(max_collector[key], data)
                    min_collector[key] = min(min_collector[key], data)
                    avg_collector[key].append(data)

    summary = {}
    for key in avg_collector.keys():
        values = avg_collector[key]
        summary[key] = {
            "min": round(min_collector[key], 4),
            "max": round(max_collector[key], 4),
            "avg": round(sum(values) / len(values), 4) if values else None
        }

    table = Table(title="PerfTrace Statistical Summary")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Min", justify="right", style="green")
    table.add_column("Max", justify="right", style="magenta")
    table.add_column("Average", justify="right", style="blue")

    for metric, vals in summary.items():
        table.add_row(
            metric,
            str(vals['min']),
            str(vals['max']),
            str(vals['avg'])
        )

    console.print(table)

def find_slowest_fastest_executed(dataframe,column_name,ascending=True):
    """Displays top 10 slowest/Fastest executed function"""
    title = 'Slowest time'
    if ascending:
        title = 'Fastest time'
    df_clean_func = dataframe.dropna(subset=[column_name])
    print(df_clean_func)
    df_clean_func = df_clean_func.sort_values(
        by="ExecutionCollector",
        ascending=ascending
    ).head(10)

    table = Table(title=title)
    table.add_column(column_name,style="green")
    table.add_column('Execution Time',style="blue")
    for _,row in df_clean_func.iterrows():
        table.add_row(str(row[column_name]),str(json.loads(row['ExecutionCollector'])['execution_time']))
    console.print(table)