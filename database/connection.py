import logging
import pymysql as MySQLdb
MySQLdb.install_as_MySQLdb()


class DatabaseConnect():
    def __init__(self, host, user, password, db_name):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def connect(self):
        try:
            db = MySQLdb.connect(host=self.host, user=self.user,
                                 password=self.password, database=self.db_name)
            return db
        except Exception as e:
            self.logger.exception("Failed to connect to database")
            raise e
