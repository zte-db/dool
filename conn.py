import os
import psycopg2
pg_user = os.getenv('DSTAT_PG_USER') or os.getenv('USER')

pg_pwd = os.getenv('DSTAT_PG_PWD')

pg_host = os.getenv('DSTAT_PG_HOST')

pg_port = os.getenv('DSTAT_PG_PORT')

class PostgresqlConn:
    """pg connection"""

    #  def __init__(self, host, port, user, password, db, schema=None):
    def __init__(self, db=None, schema=None):
        global pg_pwd
        global pg_user
        global pg_host
        global pg_port
        self.host = pg_host
        self.user = pg_user
        self.password = pg_pwd
        self.port = pg_port
        self.db = db
        self.schema=schema

    def __enter__(self):
        self.conn = psycopg2.connect(user=self.user,
                                     password=self.password, host=self.host, port=self.port)
        self.conn.set_session(autocommit=False)
        self.c = self.conn.cursor()
        return self.c

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        if self.c:
            self.c.close()
        if self.conn:
            self.conn.close()
