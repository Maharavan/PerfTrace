import os
from pathlib import Path
import sqlalchemy as db
from perftrace.storage.schema import column

class ProfilerLiteDB:
    def __init__(self,profiler_report,table_name="ProfilerReport",db_engine=None):
        self.profiler_report = profiler_report
        self.table_name = table_name
        self.db_engine = db_engine
        self.metadata = db.MetaData()
        self.table = None
        self.save_execution()


    def save_execution(self):
        with self.db_engine.connect() as conn:
            with conn.begin():
                self._create_table()
                self._insert_data(conn)
                select_stmt = db.select(self.table)
                res = conn.execute(select_stmt)
                for row in res:
                    print(row)
    def _create_table(self):
        inspect = db.inspect(self.db_engine)
        if self.table_name in inspect.get_table_names():
            self.table = db.Table(self.table_name,self.metadata,autoload_with=self.db_engine)
            return
        self.table = db.Table(self.table_name,self.metadata,*column)
        return self.metadata.create_all(self.db_engine)

    def _insert_data(self,conn):
        query = db.insert(self.table).values(**self.profiler_report)
        conn.execute(query)
        