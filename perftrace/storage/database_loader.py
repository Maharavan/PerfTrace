import pandas as pd
import duckdb
from perftrace.constant import DUCK_DB_FILE
import psycopg2
from psycopg2 import sql
from perftrace.storage.config_manager import ConfigManager
class DatabaseLoader:

    @staticmethod
    def duckdb_database_pandas_converter(tablename):
        
        sql_query = f"SELECT * FROM {tablename}"
        with duckdb.connect(database=DUCK_DB_FILE) as con:
            dataframe = con.sql(sql_query).df()
        return dataframe
    
    @staticmethod
    def postgresql_database_pandas_converter(tablename):
        config = ConfigManager.load_config()
        sql_query = sql.SQL("""
            SELECT *
            FROM {}
        """).format(
            sql.Identifier(tablename)
        )
        conn = psycopg2.connect(
            database="postgres",
            user = config.get('database').get('postgresql').get("user"),
            password = config.get('database').get('postgresql').get("password"),
            port = config.get('database').get('postgresql').get("port"),
            host= config.get('database').get('postgresql').get("host")
        )
        dataframe = pd.DataFrame()
        with conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            dataframe = pd.DataFrame(rows,columns=column_names)
        return dataframe