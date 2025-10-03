import pandas as pd
from perftrace.storage import DB_FILE,DB_TABLE_NAME
import duckdb

def database_pandas_converter():
    sql_query = f"SELECT * FROM {DB_TABLE_NAME}"
    with duckdb.connect(database=DB_FILE) as con:
        dataframe = con.sql(sql_query).df()
    return dataframe

