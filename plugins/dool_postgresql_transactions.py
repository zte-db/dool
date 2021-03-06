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
    Plugin for PostgreSQL transactions.
    """

    def __init__(self):
        self.name = 'postgresql transactions'
        self.nick = ('comm', 'roll')
        self.vars = ('commit', 'rollback')
        self.type = 'f'
        self.width = 4
        self.scale = 1
        self.last_commit = 0
        self.last_rollback = 0

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
            c.execute(
                'SELECT sum(xact_commit),sum(xact_rollback) FROM pg_stat_database;')
            row = c.fetchone()
            commit, rollback = row
            self.val[self.vars[0]] = commit-self.last_commit
            self.val[self.vars[1]] = rollback-self.last_rollback
            self.last_commit = commit
            self.last_rollback = rollback

        except Exception as e:
            print(e)
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
