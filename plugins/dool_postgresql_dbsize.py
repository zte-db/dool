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
    Plugin for PostgreSQL dbsize.
    """

    def __init__(self):
        self.name = 'postgresql dbsize'
        self.nick = ('size', 'grow', 'insert', 'update', 'delete')
        self.vars = ('dbsize', 'grow_rate', 'inserted',
                     'updated', 'deleted')
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
            c.execute("select sum(pg_database_size(oid)) from pg_database;")
            self.set2['dbsize'] = float(c.fetchone()[0])
            c.execute(
                'select sum(tup_inserted),sum(tup_updated),sum(tup_deleted) from pg_stat_database;')
            records = c.fetchone()
            for k, v in zip(['inserted', 'updated', 'deleted'], records):
                self.set2[k] = float(v)
            self.val[self.vars[0]] = self.set2['dbsize']
            self.val['grow_rate'] = (
                self.set2['dbsize'] - self.set1['dbsize']) * 1.0 / elapsed
            self.val['inserted'] = (
                self.set2['inserted'] - self.set1['inserted']) * 1.0 / elapsed
            self.val['updated'] = (
                self.set2['updated'] - self.set1['updated']) * 1.0 / elapsed
            self.val['deleted'] = (
                self.set2['deleted'] - self.set1['deleted']) * 1.0 / elapsed
            if step == op.delay:
                self.set1.update(self.set2)

        except Exception as e:
            print(e)
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
