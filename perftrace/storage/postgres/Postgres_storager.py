import json
import psycopg2
from psycopg2 import sql
from psycopg2 import errors


class PostgresSQLStorage:
    def __init__(self,profiler_report,host,port,username,password,table):
        self.profiler_report = profiler_report
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.table_name = table
        self.save_execution()

    def get_conn(self):
        conn = psycopg2.connect(
            database="postgres",
            user = self.username,
            password = self.password,
            port = self.port,
            host=self.host
        )
        return conn

    def save_execution(self):
        with self.get_conn() as conn:
            self.create_table(conn)
            self.insert_table(conn)
            conn.commit()

    
    def create_table(self,conn):
        from perftrace.storage.postgres.schema import POSTGRES_SCHEMA
        try:
            with conn.cursor() as cur:
                create_db_query = sql.SQL(POSTGRES_SCHEMA).format(sql.Identifier(self.table_name))
                cur.execute(create_db_query)
        except (Exception, errors.DatabaseError) as error:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Error while creating table failed: {error}")
            
        

    def insert_table(self,conn):
        try:
            insert_sql = sql.SQL("""
            INSERT INTO {} (
                timestamp,
                function_name,
                context_tag,
                execution_collector,
                memory_collector,
                cpu_collector,
                fileio_collector,
                garbage_collector,
                thread_context_collector,
                network_activity_collector
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """).format(sql.Identifier(self.table_name))
            data = (
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
            with conn.cursor() as cur:
                cur.execute(insert_sql,data)
        except (Exception, errors.DatabaseError) as error:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Insert failed: {error}")
        