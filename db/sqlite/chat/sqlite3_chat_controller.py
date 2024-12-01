import sqlite3
from typing import List

from db.chat_data_controller import ChatDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.chat_message import ChatMessage
from db.types.exceptions.db_error import DBError
from db.types.user import User


class SQLite3ChatController(ChatDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor):
        super().__init__(sqlite_adaptor)
        self.user_table_name = sqlite_adaptor.user_table_name
        self.chat_table_name = sqlite_adaptor.chat_table_name

    def _save_chat_message_impl(self, from_user: User, to_user: User, message: str):
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                query = f'''
                    INSERT INTO {self.chat_table_name} 
                    (chat_content, sender_id, reciever_id, message_type) 
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(query, (message, from_user.id, to_user.id, from_user.type))
                conn.commit()
        except sqlite3.IntegrityError as e:
            raise DBError("User with this username or email already exists.") from e

    def load_chat_messages(self, user: User) -> List[ChatMessage]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.chat_table_name} WHERE sender_id = ?'
            rows = cursor.execute(query, (user.id,)).fetchall()
            return [
                ChatMessage(
                    message_id=row['chat_id'],
                    sender_id=row['sender_id'],
                    receiver_id=row['receiver_id'],
                    type=row['user_password'],
                    message=row['chat_content'],
                )
                for row in rows
            ]

    def init_controller(self):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            # Chat Table (stores messages between the user and the chatbot)
            cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self.chat_table_name} (
                        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        chat_content TEXT NOT NULL,
                        sender_id INTEGER,
                        reciever_id INTEGER,-- Points to either the user or chatbot
                        message_type TEXT CHECK(message_type IN ('user', 'bot')),  -- To differentiate user and bot messages
                        FOREIGN KEY (sender_id) REFERENCES {self.user_table_name}(user_id)
                        ON DELETE CASCADE
                    )
                ''')
            conn.commit()


