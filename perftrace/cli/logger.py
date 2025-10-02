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

def get_info_about_function_context(df):
    """Get information about Function/Context"""
    if df.empty:
        print("[red] Empty result. Please provide valid command [/red]")
        return
    for _, row in df.iterrows():
        table =  Table(title="Function /Context Manager")
        table.add_column('Metrics',style="cyan", no_wrap=True)
        table.add_column('Values',style="magenta")
        for metric,results in row.items():
            table.add_row(str(metric),str(results))
        console.print(table)

def statistical_summary(dataframe):
    """Statistical Summary Average,mean,min"""
    if dataframe.empty:
        print("[red] Empty result. Please provide valid command [/red]")
        return
    dataframe_modified = dataframe.drop(['Id','Timestamp','Function_name','Context_tag'], axis=1,errors="ignore") 
    result_df = dataframe_modified.agg(['max','min','mean']).transpose().reset_index()
    result_df.columns = ['Metrics', 'Max', 'Min', 'Average']
    table =  Table(title="Function /Context Manager")
    table.add_column('Metrics',style="cyan", no_wrap=True)
    table.add_column('Max',style="magenta")
    table.add_column('Min',style="green")
    table.add_column('Average',style="blue")
    for _, row in result_df.iterrows():
        table.add_row(
            str(row['Metrics']),
            str(row['Max']),
            str(row['Min']),
            str(round(row['Average'], 2))
        )
    console.print(table)

def find_slowest_fastest_executed(dataframe,column_name,ascending=True):
    """Displays top 10 slowest/Fastest executed function"""
    title = 'Slowest time'
    if ascending:
        title = 'Fastest time'
    df_clean_func = dataframe.dropna(subset=[column_name])
    df_clean_func = df_clean_func.sort_values(
        by="ExecutionCollector_execution_time",
        ascending=ascending
    ).head(10)

    table = Table(title=title)
    table.add_column(column_name,style="green")
    table.add_column('Execution Time',style="blue")
    for _,row in df_clean_func.iterrows():
        table.add_row(str(row[column_name]),str(row['ExecutionCollector_execution_time']))
    console.print(table)