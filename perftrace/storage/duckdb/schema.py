from perftrace.storage import DB_TABLE_NAME

DUCKDB_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
    timestamp TIMESTAMP,
    function_name VARCHAR,
    context_tag VARCHAR,
    execution_collector JSON,
    memory_collector JSON,
    cpu_collector JSON,
    file_io_collector JSON,
    garbage_collector JSON,
    thread_context_collector JSON,
    network_activity_collector JSON
)
"""