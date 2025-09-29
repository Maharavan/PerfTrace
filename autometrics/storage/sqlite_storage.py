import os
from pathlib import Path
import sqlalchemy as db
class ProfilerLiteDB:
    def __init__(self,profiler_report,table_name="ProfilerReport"):
        self.db_path = Path.home() /'.autometrics'
        os.makedirs(self.db_path,exist_ok=True)
        self.db_file = os.path.join(self.db_path,'autometrics.db')
        self.db = db.create_engine(f"sqlite:///{self.db_file}")
        self.profiler_report = profiler_report
        self.table_name = table_name
        self.conn = self.db.connect()
        self.metadata = db.MetaData()
        self.table = None
        self.inspect = db.inspect(self.conn)
        self.save_execution()


    def save_execution(self):
        self.create_table()
        self.insert_data()

    def create_table(self):
        if self.table_name in self.inspect.get_table_names():
            self.table = db.Table(self.table_name,self.metadata,autoload_with=self.db)
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
        self.metadata.create_all(self.conn)
    
    def insert_data(self):
        query = db.insert(self.table).values(**self.profiler_report)
        self.conn.execute(query)
        self.conn.commit()
