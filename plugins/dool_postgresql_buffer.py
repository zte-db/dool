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
        self.name = 'postgresql buffer'
        self.nick = ('clean', 'back',
                     'alloc',
                     'heapr', 'heaph', 'ratio'
                     )
        self.vars = ('clean', 'backend',
                     'alloc',
                     'heap_blks_read', 'heap_blks_hit', 'ratio_hit',
                     )
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
            c.execute(
                "select buffers_clean,buffers_backend,buffers_alloc from pg_stat_bgwriter")
            clean, backend, alloc = c.fetchone()
            c.execute(
                "select sum(heap_blks_read), sum(heap_blks_hit) FROM pg_statio_all_tables")
            heap_blks_read, heap_blks_hit = c.fetchone()
            self.set2['heap_blks_read'] = heap_blks_read
            self.set2['heap_blks_hit'] = heap_blks_hit

            self.val[self.vars[0]] = clean
            self.val[self.vars[1]] = backend
            self.val[self.vars[2]] = alloc
            rd = (self.set2['heap_blks_read']-self.set1['heap_blks_read'])
            self.val['heap_blks_read'] = rd
            hd = (self.set2['heap_blks_hit']-self.set1['heap_blks_hit'])
            self.val['heap_blks_hit'] = hd
            self.val['ratio_hit'] = int(hd)*1.0 / (int(hd)+int(rd)+0.00001)
            if step == op.delay:
                self.set1.update(self.set2)
        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
