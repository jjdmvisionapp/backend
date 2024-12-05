import sqlite3
from sqlite3 import PARSE_DECLTYPES, PARSE_COLNAMES

from db.db_adaptor import DBAdaptor


class SQLiteDBAdaptor(DBAdaptor):

    def __init__(self, db_filename: str, **kwargs):
        # These can be optional. Check beforehand!
        self.user_table_name = kwargs.get("user_table_name")
        self.chat_table_name = kwargs.get("chat_table_name")
        self.image_table_name = kwargs.get("image_table_name")
        self.db_file_name = db_filename

    def get_connection(self):
        conn = sqlite3.connect(self.db_file_name, detect_types=PARSE_DECLTYPES | PARSE_COLNAMES)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn