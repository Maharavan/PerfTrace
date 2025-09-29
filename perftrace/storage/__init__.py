from flatten_json import flatten
from pathlib import Path
import sqlalchemy as db
from .serializer import standardize_metrics_format
from .sqlite_db.sqlite_storage import ProfilerLiteDB
import os

DB_PATH =  os.path.join(Path.home() / '.perftrace')
os.makedirs(DB_PATH,exist_ok=True)
DB_FILE = os.path.join(DB_PATH,'perftrace.db')
DB_ENGINE =  db.create_engine(f"sqlite:///{DB_FILE}")

def get_storage(backend='sqlite', report=None):
    """Factory function to get storage backend"""
    if report is None:
        report = {}
    if backend == 'sqlite':
        report = standardize_metrics_format(report)
        return ProfilerLiteDB(report,db_engine=DB_ENGINE)
    raise ValueError(f"Unknown backend: {backend}")

__all__ = ['get_storage','DB_ENGINE']

