import os
from pathlib import Path
import json
import duckdb

class DuckDBStorage:
    def __init__(self,profiler_report,table_name="ProfilerReport",db_file=None):
        self.profiler_report = profiler_report
        self.table_name = table_name
        self.db_file = db_file
        self.table = None
        self.save_execution()

    def save_execution(self):
        with duckdb.connect(database=self.db_file) as con:
            self._create_table(con)
            self._insert_data(con)
                
    def _create_table(self,con):
        from perftrace.storage.schema import TABLE_SCHEMA
        con.execute(TABLE_SCHEMA)

    def _insert_data(self,con):
        
        con.execute(
            "INSERT INTO ProfilerReport VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.profiler_report["Timestamp"],
                self.profiler_report["Function_name"],
                self.profiler_report["Context_tag"],
                json.dumps(self.profiler_report["ExecutionCollector"]) if "ExecutionCollector" in self.profiler_report else None,
                json.dumps(self.profiler_report["MemoryCollector"]) if "MemoryCollector" in self.profiler_report else None,
                json.dumps(self.profiler_report["CPUCollector"]) if "CPUCollector" in self.profiler_report else None,
                json.dumps(self.profiler_report["FileIOCollector"]) if "FileIOCollector"in self.profiler_report else None,
                json.dumps(self.profiler_report["GarbageCollector"]) if "GarbageCollector" in self.profiler_report else None,
                json.dumps(self.profiler_report["ThreadContextCollector"]) if "ThreadContextCollector" in self.profiler_report else None,
                json.dumps(self.profiler_report["NetworkActivityCollector"]) if "NetworkActivityCollector" in self.profiler_report else None,
            )
        )