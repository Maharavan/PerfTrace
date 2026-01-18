import os
from pathlib import Path
PERF_PATH =  os.path.join(Path.home() / '.perftrace')
DUCK_DB_FILE = os.path.join(PERF_PATH,'perftrace.duckdb')
CONFIG_PATH = os.path.join(PERF_PATH,'config.yml')

DEFAULT_CONFIG = {
    "database": {
        "engine": "duckdb",
        "duckdb": {
            "path": DUCK_DB_FILE,
        },
        "postgresql": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "changeme"
        }
    }
}