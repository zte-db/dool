
- [ x ] 连接数

通过pg_stat_activity系统表行数

- [ x ] 每秒执行的transaction数量(提交的和回滚的)

通过`SELECT sum(xact_commit+xact_rollback) FROM pg_stat_database;`计算总共执行的会话数量。

- [ x ] 监控cpu占用最高的pg进程
