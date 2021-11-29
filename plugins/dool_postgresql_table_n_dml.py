global pg_user
pg_user = os.getenv('DSTAT_PG_USER') or os.getenv('USER')

global pg_pwd
pg_pwd = os.getenv('DSTAT_PG_PWD')

global pg_host
pg_host = os.getenv('DSTAT_PG_HOST')

global pg_port
pg_port = os.getenv('DSTAT_PG_PORT')

global pg_database
pg_database = os.getenv('DSTAT_PG_DATABASE')

class dstat_plugin(dstat):
    """
    Plugin for PostgreSQL n_dml.
    """

    def __init__(self):
        self.name = 'postgresql table_n_dml'
        self.nick = ('time', 'db_name', 'relid', 'schemaname', 'relname','seq_scan','seq_tup_read','idx_scan',
                    'idx_tup_fetch','heap_blks_read','heap_blks_hit','n_tup_dml','relpages','n_indexes','expand_rate')
        self.vars = ['start_time','end_time', 'db_name', 'relid', 'schemaname', 'relname', 'seq_scan','seq_tup_read',
                    'idx_scan', 'idx_tup_fetch', 'heap_blks_read', 'heap_blks_hit', 'total_read','physical_read_rate',
                    'n_tup_dml','relpages_change','relpages', 'n_indexes', 'expand_rate_change', 'expand_rate']
        self.type = 'f'
        self.width = 5
        self.scale = 1
        self.last_out = []

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
            if pg_database:
                args['database'] = pg_database

            self.db = psycopg2.connect(**args)
        except Exception as e:
            raise Exception('Cannot interface with PostgreSQL server, %s' % e)

    def write_file(self, file_name, data):
        with open(file_name, 'a+') as fp:
            fp.write(data + '\n')

    def sort_result(self, key, result):
        count = 0
        for i in self.vars:
            if i == key:
                break
            count += 1
        result_ = []
        for i in range(0,len(result['relid'])):
            tmp = []
            for key in self.vars:
                tmp.append(result[key][i])
            result_.append(tmp)
        result_.sort(key=lambda x:x[count], reverse=True)
        res = self.completion_result(result_)
        return res

    def completion_result(self, result):
        hh = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        length = len(result)
        if length < 50:
            delta = 50 - length
            for i in range(0, delta):
                result.append(hh)
            return result
        else:
            res = []
            for i in range(0,50):
                res.append(result[i])       
            return res

    def extract(self, outputfile):
        try:
            import os,sys
            except_line = ['time', 'db_name', 'relid', 'schemaname', 'relpages',
                           'relname', 'n_indexes','expand_rate']
            c = self.db.cursor()
            sql = '''
            select ceil(extract(epoch from now())) as time,current_database() as db_name,t.relid,t.schemaname,t.relname,s.seq_scan,s.seq_tup_read,s.idx_scan,s.idx_tup_fetch,t.heap_blks_read,t.heap_blks_hit,(s.n_tup_ins+s.n_tup_upd+s.n_tup_del) as n_tup_dml,c.relpages,d.n_indexes,
                (case when c.relpages>1 then (100-c.reltuples::bigint*(i.stawidth::bigint+26)*100/(c.relpages::bigint*8*1024)) else 0 end) as expand_rate
                from 
                pg_class c,pg_statio_all_tables t ,pg_stat_all_tables s ,(select starelid,sum(stawidth) as stawidth from pg_statistic group by starelid) as i,(select indrelid,count(1) as n_indexes from pg_index group by indrelid) as d
                where 
                c.oid=s.relid 
                and c.oid=t.relid
                and c.oid=i.starelid
                and c.oid=d.indrelid 
                and t.schemaname not in ('statsrepo','statsinfo','pg_catalog','pg_toast','information_schema') 
                order by relid asc;
            '''
            c.execute(sql)
            output = c.fetchall()
            out_dict = {
                'time':[],
                'db_name':[], 
                'relid':[], 
                'schemaname':[], 
                'relname':[],
                'seq_scan':[],
                'seq_tup_read':[],
                'idx_scan':[],
                'idx_tup_fetch':[],
                'heap_blks_read':[],
                'heap_blks_hit':[],
                'n_tup_dml':[],
                'relpages':[],
                'n_indexes':[],
                'expand_rate':[]
            }

            result = {
                'start_time':[],
                'end_time':[],
                'db_name':[], 
                'relid':[], 
                'schemaname':[], 
                'relname':[],
                'seq_scan':[],
                'seq_tup_read':[],
                'idx_scan':[],
                'idx_tup_fetch':[],
                'heap_blks_read':[],
                'heap_blks_hit':[],
                'total_read':[],
                'physical_read_rate':[],
                'n_tup_dml':[],
                'relpages_change':[],
                'relpages':[],
                'n_indexes':[],
                'expand_rate_change':[],
                'expand_rate':[]
            }

            result_list = ['time', 'db_name', 'relid', 'schemaname', 'relname', 'seq_scan','seq_tup_read',
                           'idx_scan', 'idx_tup_fetch', 'heap_blks_read', 'heap_blks_hit', 'n_tup_dml',
                           'relpages', 'n_indexes', 'expand_rate']


            for i in output:
                for count in range(0, len(self.nick)):
                    if count == 0:
                        time = str(i[count])
                        out_dict[self.nick[count]].append(time)
                    else:
                        out_dict[self.nick[count]].append(i[count])

            if self.last_out == []:
                pass
            else:
                last_output = self.last_out

                for i in range(0,len(out_dict['relid'])):
                    for key in except_line:
                        if key != 'time':
                            result[key].append(out_dict[key][i])

                    if out_dict['relid'][i] not in last_output['relid']:
                        # new record
                        for key in result_list:
                            if key in except_line:
                                pass
                            else:
                                result[key].append(out_dict[key][i])
                        result['start_time'].append(out_dict['time'][i])
                        result['end_time'].append(out_dict['time'][i])
                        result['expand_rate_change'].append(0)
                        result['relpages'].append(0)
                    else:
                        # old record
                        last_count = 0
                        for key in last_output['relid']:
                            if out_dict['relid'][i] == key:
                                break
                            last_count += 1
                        result['start_time'].append(last_output['time'][last_count])
                        result['end_time'].append(out_dict['time'][i])
                        for key in result_list:
                            if key in except_line:
                                pass
                            else:
                                res = out_dict[key][i] - last_output[key][last_count]
                                result[key].append(res)
                        result['expand_rate_change'].append(out_dict['expand_rate'][i] - last_output['expand_rate'][last_count])
                        result['relpages_change'].append(out_dict['relpages'][i] - last_output['relpages'][last_count])
                        
                    blks = out_dict['heap_blks_read'][i] + out_dict['heap_blks_hit'][i]
                    result['total_read'].append(blks)
                    if blks == 0:
                        result['physical_read_rate'].append(0)
                    else:
                        result['physical_read_rate'].append(out_dict['heap_blks_read'][i] * 100 / blks)

                n_dml_ = self.sort_result('n_tup_dml', result)

                line1 = '-----------------------------------------------------------------------------postgresql-table_n_dml----------------------------------------------------------------------------'
                line2 = ''
                for i in self.vars:
                    line2 += i + '  '
                self.write_file(outputfile,'\n')
                self.write_file(outputfile,line1)
                self.write_file(outputfile,line2)
                for i in n_dml_:
                    t = ''
                    c = 0
                    for j in i:
                        if c != len(i) - 1:
                            t += str(j) + ', '
                        else:
                            t += str(j)
                        c += 1
                    self.write_file(outputfile,t)

            self.last_out = out_dict

        except Exception as e:
            print(e)
            self.last_out = []
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
