import os
from pathlib import Path
import sqlalchemy as db
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
                self._create_table(conn)
                self._insert_data(conn)

    def _create_table(self,conn):
        inspect = db.inspect(self.db_engine)
        if self.table_name in inspect.get_table_names():
            self.table = db.Table(self.table_name,self.metadata,autoload_with=self.db_engine)
            return
        columns = [db.Column('Id', db.Integer,primary_key=True,autoincrement=True)]

        for column,values in self.profiler_report.items():
            type = None
            if isinstance(values,int):
                type = db.Integer
            elif isinstance(values,float):
                type = db.Float
            else:
                type = db.String
            
            columns.append(db.Column(column,type))
        self.table = db.Table(self.table_name,self.metadata,*columns)
        self.metadata.create_all(self.db_engine)
    
    def _insert_data(self,conn):
        query = db.insert(self.table).values(**self.profiler_report)
        conn.execute(query)
    
    
