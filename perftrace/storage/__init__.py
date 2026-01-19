from flatten_json import flatten
from pathlib import Path
from .duckdb.duckdb_storager import DuckDBStorage
from .postgres.Postgres_storager import PostgresSQLStorage
from perftrace.storage.config_manager import ConfigManager
import os

DB_TABLE_NAME = 'ProfilerReport'


def get_storage(backend='duckdb',report=None):
    """Factory function to get storage backend"""
    config = ConfigManager.load_config()
    database_name = config.get('database').get('engine',"")
    if report is None:
        report = {}
    if database_name.lower() == 'duckdb':
        db_path = config.get('database').get('duckdb').get("path")
        return DuckDBStorage(report,table_name=DB_TABLE_NAME,db_file=db_path)
    elif database_name.lower() == 'postgresql':
        host = config.get('database').get('postgresql').get("host")
        port = config.get('database').get('postgresql').get("port")
        username = config.get('database').get('postgresql').get("user")
        password = config.get('database').get('postgresql').get("password")
        return PostgresSQLStorage(report,host,port,username,password,DB_TABLE_NAME)

    raise ValueError(f"Unknown backend: {backend}")

__all__ = ['get_storage','DB_TABLE_NAME','DB_FILE']

