from flatten_json import flatten
from pathlib import Path
import sqlalchemy as db
from .duckdb.duckdb_storager import DuckDBStorage
from perftrace.constant import DUCK_DB_FILE
from perftrace.storage.config_manager import ConfigManager
import os

def get_storage(backend='duckdb',report=None):
    """Factory function to get storage backend"""
    config = ConfigManager.load_config()
    database_name = config.get('database').get('engine',"")
    if report is None:
        report = {}
    if database_name.lower() == 'duckdb':
        DB_TABLE_NAME = 'ProfilerReport'
        return DuckDBStorage(report,table_name=DB_TABLE_NAME,db_file=DUCK_DB_FILE)
    elif database_name.lower() == 'postgresql':
        pass
    raise ValueError(f"Unknown backend: {backend}")

__all__ = ['get_storage','DB_TABLE_NAME','DB_FILE']

