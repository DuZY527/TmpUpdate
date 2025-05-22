import os
from urllib.parse import quote_plus

mysql_host = 'mysql-primary.ceis-mysql.svc.cluster.local'
env_mysql_host = os.getenv('MYSQL_HOST')
if env_mysql_host is not None:
    mysql_host = env_mysql_host

# 数据库选择：生产用mysql， 本地用sqlite
if os.name == 'nt':  # window 一般是学生使用,这里默认给sqlite
    db_type = 'sqlite'
else:
    db_type = 'mysql'

if db_type == 'mysql':
    DB_CONNECTION_STRING = f"mysql+pymysql://root:{quote_plus('root@mysql!123')}@{mysql_host}/ceis-algorithm?charset=utf8"
else:
    DB_CONNECTION_STRING = "sqlite:///ceis-algorithm.db"
