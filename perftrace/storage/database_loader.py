from sqlalchemy import create_engine
import pandas as pd
from perftrace.storage import SQLITE_DB_ENGINE,SQLITE_TABLE_NAME


def database_pandas_converter():
    sql_query = f"SELECT * FROM {SQLITE_TABLE_NAME}"
    df = pd.read_sql_table(SQLITE_TABLE_NAME,SQLITE_DB_ENGINE)
    return df
