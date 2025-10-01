import pandas as pd
from rich import print

def filter_functions_context(df,column_value):
    remove_duplicates = set()
    for function_name in df[column_value]:
        if function_name not in remove_duplicates and function_name is not None:
            print(f"[green]{function_name}[/green]")
        if function_name is not None:
            remove_duplicates.add(function_name)
    if not remove_duplicates:
        print(f"[red]No info available[/red]")

def get_info_about_function_context(df,function_name):
    for ind,row in df.iterrows():
        if function_name in str(row['Function_name']):
            print(row)
