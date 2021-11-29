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
        self.name = 'postgresql sql_io_time'
        self.nick = ('start_time','end_time','io_time','rolname','dbname','calls','total_time','mean_time','blk_read_time','blk_write_time','queryid','query', )
        self.vars = self.nick
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

    def write_file(self,file_name,data):
        with open(file_name, 'a+') as fp:
            fp.write(data + '\n')

    def extract(self,outputfile):
        try:
            c = self.db.cursor()
            sql='''select snapid from statsrepo.snapshot where time>now()-interval '20 mins' order by snapid desc limit 2;'''
            c.execute(sql)
            out = c.fetchall()
            snapid = [out[1][0], out[0][0]]

            sql = '''
            SELECT
                ceil(extract(epoch from start_time)) as start_time,
                ceil(extract(epoch from end_time)) as end_time,
                ((t1.blk_read_time + t1.blk_write_time) / t1.calls)::numeric(1000, 3) AS io_time,
                t1.rolname::text,
                t1.dbname::name,
                t1.calls,
                t1.total_time::numeric(1000, 3),
                (t1.total_time / t1.calls)::numeric(1000, 3) as mean_time,
                t1.blk_read_time::numeric(1000, 3),
                t1.blk_write_time::numeric(1000, 3),
                t1.queryid,
                substr(t1.query,1,2000) as query
            FROM
                (SELECT
                    st1.start_time,
                    st2.end_time,
                    rol.name AS rolname,
                    db.name AS dbname,
                    st2.query,
                    st2.queryid,
                    statsrepo.sub(st2.calls, st1.calls) AS calls,
                    statsrepo.sub(st2.total_time, st1.total_time) AS total_time,
                    statsrepo.sub(st2.blk_read_time, st1.blk_read_time) AS blk_read_time,
                    statsrepo.sub(st2.blk_write_time, st1.blk_write_time) AS blk_write_time
                FROM
                    (SELECT
                        s.snapid,
                        s.dbid,
                        s.userid,
                        s.queryid,
                        s.query,
                        s.calls,
                        s.total_time,
                        s.blk_read_time,
                        s.blk_write_time,
                        ss.time as end_time
                    FROM
                        statsrepo.statement s
                        JOIN statsrepo.snapshot ss ON (ss.snapid = s.snapid)
                    WHERE
                        s.snapid = %s 
                        AND ss.instid = (SELECT instid FROM statsrepo.snapshot ss1 WHERE ss1.snapid = %s)
                    ) AS st2
                    LEFT JOIN (SELECT
                        s.snapid,
                        s.dbid,
                        s.userid,
                        s.queryid,
                        s.query,
                        s.calls,
                        s.total_time,
                        s.blk_read_time,
                        s.blk_write_time,
                        ss.time as start_time
                    FROM
                        statsrepo.statement s
                        JOIN statsrepo.snapshot ss ON (ss.snapid = s.snapid)
                    WHERE
                        s.snapid = %s 
                        AND ss.instid = (SELECT instid FROM statsrepo.snapshot ss1 WHERE ss1.snapid = %s)
                    ) AS st1 ON 
                        (st1.dbid = st2.dbid AND st1.userid = st2.userid AND
                        st1.queryid = st2.queryid )
                    JOIN statsrepo.database db ON
                        (db.snapid = st2.snapid AND db.dbid = st2.dbid)
                    JOIN statsrepo.role rol ON
                        (rol.snapid = st2.snapid AND rol.userid = st2.userid)
                ) AS t1
            WHERE t1.calls > 0 and t1.total_time > 0
            ORDER BY
                1 DESC,
                5 DESC limit 30;
            ''' % (snapid[1], snapid[1], snapid[0], snapid[1])
            c.execute(sql)
            # io_time,rolname,dbname,calls,total_time,mean_time,blk_read_time,blk_write_time,query = c.fetchall()
            output = c.fetchall()

            line1 = '-----------------------------------------------------------------------------postgresql-sql_io_time----------------------------------------------------------------------------'
            line2 = 'start_time       end_time        io_time         rolname          dbname          calls         total_time      mean_time     blk_read_time   blk_write_time      queryid      query     '
            self.write_file(outputfile,'\n')
            self.write_file(outputfile,line1)
            self.write_file(outputfile,line2)

            if output == []:
                for name in self.vars:
                    self.val[name] = -1
            else:
                for a in output:
                    aa = ''
                    for p in a:
                        t = str(p)
                        aa += t.replace('\n',' ').replace('\t',' ') + ','
                    self.write_file(outputfile, aa)

            length = len(output)
            if length < 30 and length >= 1:
                hh = output[0]
                start_time = str(hh[0])
                end_time = str(hh[1])
                shuchu = start_time + ',' + end_time + ',0,0,0,0,0,0,0,0,0,'
                for i in range(length,30):
                    self.write_file(outputfile, shuchu)

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
