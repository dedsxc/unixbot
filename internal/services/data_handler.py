from internal.services.database import Database


class DataHandler:
    def __init__(self, db_name, table, column_name):
        self.db = Database(db_name)
        self.table = table
        self.column_name = column_name

    def create_table(self):
        columns = 'id INTEGER PRIMARY KEY, {} TEXT'.format(self.column_name)
        self.db.create_table(self.table, columns)

    def insert_data(self, data):
        self.db.insert_data(self.table, self.column_name, data)

    def check_data_exist(self, data):
        existing_data = self.db.select_data(self.table, self.column_name, data)
        if not existing_data:
            return False
        else:
            return True
