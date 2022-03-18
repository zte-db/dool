#!/bin/bash

过去的采集数据：

'''sh
./dool -a  -i -r -s  --aio --fs --ipc --lock --raw --socket --tcp --udp --unix --vm --vm-adv --zones --postgresql-backup --postgresql-dbsize --postgresql-log --postgresql-conn --postgresql-locks --postgresql-transactions --postgresql-buffer --output metrics.csv
'''

新的采集数据：

需要先安装pg_statsinfo

'''sh
./dool1 --postgresql-time -a -s -i -r --aio --fs --ipc --lock --raw --socket --tcp --udp --unix --vm --vm-adv --zones --postgresql-all --postgresql-conn --postgresql-lockwaits --postgresql-settings --output ./metrics1.csv --noupdate 5

./dool2 --postgresql-sql-total-time --postgresql-sql-mean-time --postgresql-sql-calls --postgresql-sql-io-time --output2 ./metrics2.csv --postgresql-table-n-dml --postgresql-table-expand-rate --postgresql-table-pyhsical-read --postgresql-table-seq-read --output3 ./metrics3.csv --noupdate 20
'''
