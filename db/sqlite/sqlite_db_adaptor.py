import sqlite3

from db.db_adaptor import DBAdaptor


class SQLiteDBAdaptor(DBAdaptor):

    def __init__(self, db_file_name: str, user_table_name: str, chat_table_name: str):
        super().__init__(user_table_name, chat_table_name)
        self.db_file_name = db_file_name

    def get_connection(self):
        conn = sqlite3.connect(self.db_file_name)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        return conn