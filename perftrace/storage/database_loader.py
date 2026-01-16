import pandas as pd
from perftrace.constant import DUCK_DB_FILE
import duckdb

class DatabaseLoader:

    @staticmethod
    def duckdb_database_pandas_converter(tablename):
        
        sql_query = f"SELECT * FROM {tablename}"
        with duckdb.connect(database=DUCK_DB_FILE) as con:
            dataframe = con.sql(sql_query).df()
        return dataframe