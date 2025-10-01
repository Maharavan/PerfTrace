from flatten_json import flatten
from pathlib import Path
import sqlalchemy as db
from .serializer import standardize_metrics_format
from .sqlite_db.sqlite_storage import ProfilerLiteDB
import os

SQLITE_DB_PATH =  os.path.join(Path.home() / '.perftrace')
os.makedirs(SQLITE_DB_PATH,exist_ok=True)
SQLITE_DB_FILE = os.path.join(SQLITE_DB_PATH,'perftrace.db')
SQLITE_DB_ENGINE =  db.create_engine(f"sqlite:///{SQLITE_DB_FILE}")
SQLITE_TABLE_NAME = 'ProfilerReport'
def get_storage(backend='sqlite',report=None):
    """Factory function to get storage backend"""
    if report is None:
        report = {}
    report = standardize_metrics_format(report)
    if backend == 'sqlite':
        return ProfilerLiteDB(report,table_name=SQLITE_TABLE_NAME,db_engine=SQLITE_DB_ENGINE)
    raise ValueError(f"Unknown backend: {backend}")

__all__ = ['get_storage','SQLITE_DB_ENGINE','SQLITE_TABLE_NAME']

