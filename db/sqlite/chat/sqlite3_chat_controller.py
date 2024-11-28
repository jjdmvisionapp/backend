from db.chat_data_controller import ChatDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.user import User


class SQLite3ChatController(ChatDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor):
        super().__init__(sqlite_adaptor)
        self.user_table_name = sqlite_adaptor.user_table_name
        self.chat_table_name = sqlite_adaptor.chat_table_name

    def _save_chat_message_impl(self, from_user: User, to_user: User, message: str):
        pass

    def init_controller(self):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            # Chat Table (stores messages between the user and the chatbot)
            cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self.chat_table_name} (
                        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        chat_content TEXT NOT NULL,
                        sender_id INTEGER,  -- Points to either the user or chatbot
                        message_type TEXT CHECK(message_type IN ('user', 'bot')),  -- To differentiate user and bot messages
                        FOREIGN KEY (sender_id) REFERENCES {self.user_table_name}(user_id)
                        ON DELETE CASCADE
                    )
                ''')
            conn.commit()


