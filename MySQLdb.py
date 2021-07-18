import pymysql
def connect(host,port,user,passwd):
    port=int(port)
    conn = pymysql.connect(host=host,port=port,user=user, password=passwd)
    return conn

