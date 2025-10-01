from sqlalchemy import  Column, Integer, Float,String

column = [
    Column("Id", Integer, primary_key=True, autoincrement=True),
    # Memory
    Column("Function_name",String),
    Column("Context_tag",String),

    Column("MemoryCollector_current_memory", Integer),
    Column("MemoryCollector_peak_memory", Integer),

    # CPU
    Column("CPUCollector_ram_delta", Float),
    Column("CPUCollector_start_ram", Float),
    Column("CPUCollector_end_ram", Float),
    Column("CPUCollector_avg_cpu_percentage", Float),
    Column("CPUCollector_cpu_usage_start", Float),
    Column("CPUCollector_cpu_usage_end", Float),

    # Execution
    Column("ExecutionCollector_execution_time", Float),
    Column("ExecutionCollector_start_time", Float),
    Column("ExecutionCollector_end_time", Float),

    # File IO
    Column("FileIOCollector_read_bytes", Integer),
    Column("FileIOCollector_write_bytes", Integer),
    Column("FileIOCollector_read_count", Integer),
    Column("FileIOCollector_write_count", Integer),
    Column("FileIOCollector_other_count", Integer),
    Column("FileIOCollector_other_bytes", Integer),

    # Garbage Collector
    Column("GarbageCollector_initial_gc_count_0", Integer),
    Column("GarbageCollector_initial_gc_count_1", Integer),
    Column("GarbageCollector_initial_gc_count_2", Integer),
    Column("GarbageCollector_final_gc_count_0", Integer),
    Column("GarbageCollector_final_gc_count_1", Integer),
    Column("GarbageCollector_final_gc_count_2", Integer),
    Column("GarbageCollector_delta_gc_count_0", Integer),
    Column("GarbageCollector_delta_gc_count_1", Integer),
    Column("GarbageCollector_delta_gc_count_2", Integer),

    # Threads
    Column("ThreadContextCollector_threads_delta", Integer),
    Column("ThreadContextCollector_ctx_switches_voluntary_delta", Integer),
    Column("ThreadContextCollector_ctx_switches_involuntary_delta", Integer),
    Column("ThreadContextCollector_initial_threads", Integer),
    Column("ThreadContextCollector_final_threads", Integer),
    Column("ThreadContextCollector_initial_ctx_switches_voluntary", Integer),
    Column("ThreadContextCollector_initial_ctx_switches_involuntary", Integer),
    Column("ThreadContextCollector_final_ctx_switches_voluntary", Integer),
    Column("ThreadContextCollector_final_ctx_switches_involuntary", Integer),

    # Network
    Column("NetworkActivityCollector_tcp_connection_delta", Integer),
    Column("NetworkActivityCollector_udp_connection_delta", Integer),
    Column("NetworkActivityCollector_tcp_connection", Integer),
    Column("NetworkActivityCollector_udp_connection", Integer),
    Column("NetworkActivityCollector_bytes_sent", Integer),
    Column("NetworkActivityCollector_bytes_received", Integer),
    Column("NetworkActivityCollector_bytes_sent_delta", Integer),
    Column("NetworkActivityCollector_bytes_received_delta", Integer),
    Column("NetworkActivityCollector_connection_type_TIME_WAIT", Integer),
    Column("NetworkActivityCollector_connection_type_LISTEN", Integer),
    Column("NetworkActivityCollector_connection_type_ESTABLISHED", Integer),
    Column("NetworkActivityCollector_connection_type_NONE", Integer),
    Column("NetworkActivityCollector_connection_type_SYN_SENT", Integer),
    Column("NetworkActivityCollector_connection_type_CLOSE_WAIT",Integer)
]
    
