from perftrace.storage import DB_TABLE_NAME

TABLE_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
    Timestamp TIMESTAMP,
    Function_name VARCHAR,
    Context_tag VARCHAR,
    ExecutionCollector JSON,
    MemoryCollector JSON,
    CPUCollector JSON,
    FileIOCollector JSON,
    GarbageCollector JSON,
    ThreadContextCollector JSON,
    NetworkActivityCollector JSON
)
"""