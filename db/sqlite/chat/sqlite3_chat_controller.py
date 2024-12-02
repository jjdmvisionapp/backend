import sqlite3
from typing import List

from chatbots.chatbot_controller import ChatBotController
from db.chat_data_controller import ChatDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.chat_message import ChatMessage
from db.types.exceptions.db_error import DBError
from db.types.user.user_container import UserContainer

# ChatGPT helped add timestamp
class SQLite3ChatController(ChatDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor, chatbot: ChatBotController):
        super().__init__(sqlite_adaptor, chatbot)
        self.user_table_name = sqlite_adaptor.user_table_name
        self.chat_table_name = sqlite_adaptor.chat_table_name

    def _save_chat_message_impl(self, from_user: UserContainer, to_user: UserContainer, message: str, message_type: str):
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                query = f'''
                    INSERT INTO {self.chat_table_name} 
                    (chat_content, sender_id, to_id, message_type) 
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(query, (message, from_user.id, to_user.id if to_user else None, message_type))
                conn.commit()
        except sqlite3.IntegrityError as e:
            raise DBError("Failed to save chat message due to database integrity error.") from e

    def load_chat_messages(self, user: UserContainer) -> List[ChatMessage]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'''
                SELECT * FROM {self.chat_table_name} 
                WHERE sender_id = ? OR to_id = ?
                ORDER BY chat_timestamp
            '''
            rows = cursor.execute(query, (user.id, user.id)).fetchall()
            return [
                ChatMessage(
                    message_id=row['chat_id'],
                    sender_id=row['sender_id'],
                    receiver_id=row['to_id'],
                    type=row['message_type'],
                    message=row['chat_content'],
                    timestamp=row['chat_timestamp'],
                )
                for row in rows
            ]

    def init_controller(self):
        super().init_controller()
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            # Chat Table (stores messages between the user and the chatbot)
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.chat_table_name} (
                    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    chat_content TEXT NOT NULL,
                    sender_id INTEGER,
                    to_id INTEGER, -- Points to either the user or chatbot
                    message_type TEXT CHECK(message_type IN ('user', 'bot')),  -- To differentiate user and bot messages
                    FOREIGN KEY (sender_id) REFERENCES {self.user_table_name}(user_id)
                    ON DELETE CASCADE,
                    FOREIGN KEY (to_id) REFERENCES {self.user_table_name}(user_id)
                    ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def delete_chat_message(self, message_id: int):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            delete_query = f'DELETE FROM {self.chat_table_name} WHERE chat_id = ?'
            cursor.execute(delete_query, (message_id,))
            conn.commit()
