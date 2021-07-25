### Authority: Dag Wieers <dag@wieers.com>

class dstat_plugin(dstat):
    """
    Most expensive CPU process.

    Displays the postgresql process that uses the CPU the most during the monitored
    interval. The value displayed is the percentage of CPU time for the total
    amount of CPU processing power. Based on per process CPU information.
    """
    def __init__(self):
        self.name = 'postgresql_cpu'
        self.vars = ('postgresql_cpu',)
        self.type = 's'
        self.width = 16
        self.scale = 0
        self.pidset1 = {}; self.pidset2 = {}

    def extract(self):
        self.val['max'] = 0
        self.val['postgresql_cpu'] = '%s' % (cprint(0.0, 'f', 3, 3))
        for pid in proc_pidlist():
            try:
                ### Using dopen() will cause too many open files
                l = proc_splitline('/proc/%s/stat' % pid)
            except IOError:
                continue

            if len(l) < 15: continue

            ### Reset previous value if it doesn't exist
            if pid not in self.pidset1:
                self.pidset1[pid] = 0

            self.pidset2[pid] = int(l[13]) + int(l[14])
            usage = (self.pidset2[pid] - self.pidset1[pid]) * 1.0 / elapsed / cpunr
            name = l[1][1:-1]
            proc_name = getnamebypid(pid, name)
            ### Is it a new topper ?
            if usage < self.val['max'] or not proc_name.startswith("postgresql"):
                continue
            self.val['max'] = usage
            self.val['pid'] = pid
            self.val['name'] = proc_name

        self.val['postgresql_cpu'] = '%s' % (cprint(self.val['max'], 'f', 3, 34))

        ### Debug (show PID)
#        self.val['cpu process'] = '%*s %-*s' % (5, self.val['pid'], self.width-6, self.val['name'])

        if step == op.delay:
            self.pidset1.update(self.pidset2)

    def showcsv(self):
        return '%d' % (self.val['max'])

# vim:ts=4:sw=4:et
