import sqlite3
from common.logger import log

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        try:
            query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})'
            self.cursor.execute(query)
            self.conn.commit()
            log.info(f"[database][create_table] table {table_name} created")
        except Exception as e:
            log.error(f"[database][create_table]  error creating table: {e}")

    def insert_data(self, table_name, column, values):
        try:
            query = "INSERT INTO {} ({}) VALUES ('{}')".format(table_name, column, values)
            self.cursor.execute(query)
            self.conn.commit()
            log.info(f"[database][insert_data] insert data successfully")
        except Exception as e:
            log.error(f"[database][insert_data] error insert data: {e}")
            log.error(f"[database][insert_data] query: {query}")

    def select_data(self, table_name, column, value):
        try:
            query = f'SELECT * FROM {table_name} WHERE {column} = "{value}"'
            self.cursor.execute(query)
            log.debug(f"[database][select_data] query: {query}")
            return self.cursor.fetchall()
        except Exception as e:
            log.error(f"[database][select_data] error select data: {e}")