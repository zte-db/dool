global pg_user
pg_user = os.getenv('DSTAT_PG_USER') or os.getenv('USER')

global pg_pwd
pg_pwd = os.getenv('DSTAT_PG_PWD')

global pg_host
pg_host = os.getenv('DSTAT_PG_HOST')

global pg_port
pg_port = os.getenv('DSTAT_PG_PORT')


class dstat_plugin(dstat):
    """
    Plugin for PostgreSQL connections.
    """

    def __init__(self):
        self.name = 'postgresql conn'
        self.nick = ('ThCon', '%Con')
        self.vars = ('Threads_connected', 'Threads')
        self.type = 'f'
        self.width = 4
        self.scale = 1

    def check(self): 
        global psycopg2
        import psycopg2
        try:
            args = {}
            if pg_user:
                args['user'] = pg_user
            if pg_pwd:
                args['password'] = pg_pwd
            if pg_host:
                args['host'] = pg_host
            if pg_port:
                args['port'] = pg_port

            self.db = psycopg2.connect(**args)
        except Exception as e:
            raise Exception('Cannot interface with PostgreSQL server, %s' % e)

    def extract(self):
        try:
            c = self.db.cursor()
            c.execute("select count(*) used from pg_stat_activity")
            conn_cnt=c.fetchone()[0]
            c.execute("select setting::int max_conn from pg_settings where name=$$max_connections$$")
            max_conn = c.fetchone()[0]
            c.execute("select setting::int res_for_super from pg_settings where name=$$superuser_reserved_connections$$")
            res_for_super_conn = c.fetchone()[0]
            self.val[self.vars[0]] = conn_cnt
            self.val[self.vars[1]] = conn_cnt/max_conn

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
