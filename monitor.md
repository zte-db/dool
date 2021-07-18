# 数据库性能监测

监测mysql和postgresql示例
```
docker pull mysql:5.7
docker run --name dool-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:5.7

mysql -P 3306 -u root -h 127.0.0.1  -p

export DSTAT_MYSQL_USER=root
export DSTAT_MYSQL_PWD=my-secret-pw
export DSTAT_MYSQL_HOST=127.0.0.1
export DSTAT_MYSQL_PORT=3306


docker run --name dool-pg -p 5432:5432 -e POSTGRES_PASSWORD=my-secret-pw -d postgres:12
psql -h 127.0.0.1 -p 5432 -U postgres

export DSTAT_PG_USER=postgres
export DSTAT_PG_PWD=my-secret-pw
export DSTAT_PG_HOST=127.0.0.1
export DSTAT_PG_PORT=5432
```

```
./dool --mysql5-conn
./dool --postgresql-conn
```
