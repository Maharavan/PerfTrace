from flatten_json import flatten
from pathlib import Path
import sqlalchemy as db
from .duckdb.duckdb_storager import DuckDBStorage
import os

DB_PATH =  os.path.join(Path.home() / '.perftrace')
os.makedirs(DB_PATH,exist_ok=True)
DB_TABLE_NAME = 'ProfilerReport'
DB_FILE = os.path.join(DB_PATH,'perftrace.duckdb')
def get_storage(backend='duckdb',report=None):
    """Factory function to get storage backend"""
    if report is None:
        report = {}
    if backend == 'duckdb':
        return DuckDBStorage(report,table_name=DB_TABLE_NAME,db_file=DB_FILE)
    raise ValueError(f"Unknown backend: {backend}")

__all__ = ['get_storage','DB_TABLE_NAME','DB_FILE']

