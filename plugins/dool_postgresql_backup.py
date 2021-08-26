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
        self.name = 'postgresql backup'
        self.nick = ('Delay',)
        self.vars = ('backup_delay',)
        self.type = 'f'
        self.width = 5
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
            sql='''select application_name,
            client_addr,client_hostname,
            client_port,state,
            sync_priority,sync_state,
            pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) 
            from 
            pg_stat_replication;
            '''
            c.execute(sql)
            delay = c.fetchone()[0]
            self.val[self.vars[0]] = delay

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
