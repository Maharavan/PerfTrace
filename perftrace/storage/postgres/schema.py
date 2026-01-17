POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS {} (
    timestamp TIMESTAMP,
    Function_name TEXT,
    context_tag TEXT,
    execution_collector JSONB,
    memory_collector JSONB,
    cpu_collector JSONB,
    fileio_collector JSONB,
    garbage_collector JSONB,
    thread_context_collector JSONB,
    network_activity_collector JSONB
);
"""