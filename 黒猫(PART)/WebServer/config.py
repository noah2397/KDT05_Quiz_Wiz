import os

# 다양한 DBMS URI
BASE_DIR = os.path.dirname(__file__)
DB_NAME_SQLITE = 'app.db'

# 다양한 DBMS URI
DB_SQLITE_URI = f'sqlite:///{os.path.join(BASE_DIR, DB_NAME_SQLITE)}'
DB_MYSQL_URI = 'mysql+pymysql://root:1234@localhost/quiz_wiz'

# 사용할 DBMS 설정(얘들은 이름이 고정이다)
#SQLALCHEMY_DATABASE_URI = DB_SQLITE_URI
SQLALCHEMY_DATABASE_URI =DB_MYSQL_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

DB_USER_ID='root'