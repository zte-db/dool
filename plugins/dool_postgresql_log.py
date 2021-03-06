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
    Plugin for PostgreSQL log.
    """

    def __init__(self):
        self.name = 'postgresql log'
        self.nick = ('WAL',)
        self.vars = ('wal',)
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
            c.execute('select pg_current_wal_lsn();')
            self.set2['wal'] = c.fetchone()[0]
            wal1 = self.set1['wal']
            wal2 = self.set2['wal']
            if wal1 != 0:
                sql = "select pg_wal_lsn_diff('{}', '{}')".format(wal2, wal1)
                c.execute(sql)
                waldiff = c.fetchone()[0]/elapsed
            else:
                waldiff = 0
            self.val['wal'] = waldiff
            #  self.val['wal'] = (self.set2['wal'] - self.set1['wal']) * 1.0 / elapsed
            if step == op.delay:
                self.set1.update(self.set2)

        except Exception as e:
            print(e)
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
