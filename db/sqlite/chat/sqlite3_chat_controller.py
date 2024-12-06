import sqlite3
from datetime import datetime
from typing import List

from chatbots.chatbot_controller import ChatBotController
from db.chat_data_controller import ChatDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.chat_message import ChatMessage
from db.types.exceptions.db_error import DBError
from db.types.user.user_container import UserContainer

class SQLite3ChatController(ChatDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor, chatbot: ChatBotController):
        super().__init__(sqlite_adaptor, chatbot)
        self.user_table_name = sqlite_adaptor.user_table_name
        self.chat_table_name = sqlite_adaptor.chat_table_name

    def _save_chat_message_impl(self, from_user: UserContainer, to_user: UserContainer, message: str, message_type: str) -> ChatMessage:
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()

                # First, ensure the sender exists in the user table
                cursor.execute(f"SELECT user_id FROM {self.user_table_name} WHERE user_id = ?", (from_user.id,))
                sender_exists = cursor.fetchone()
                if not sender_exists:
                    raise DBError(f"Sender user with id {from_user.id} does not exist.")

                # If to_user exists, ensure they also exist in the user table
                if to_user:
                    cursor.execute(f"SELECT user_id FROM {self.user_table_name} WHERE user_id = ?", (to_user.id,))
                    receiver_exists = cursor.fetchone()
                    if not receiver_exists:
                        raise DBError(f"Receiver user with id {to_user.id} does not exist.")
                else:
                    receiver_exists = True  # If there's no receiver, assume valid for chatbot

                # Insert the message into the chat table
                query = f'''
                    INSERT INTO {self.chat_table_name} 
                    (chat_content, sender_id, to_id, message_type) 
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(query, (message, from_user.id, to_user.id if to_user else -1, message_type))

                # Fetch the timestamp for the inserted row
                last_row_id = cursor.lastrowid
                timestamp_query = f'''
                    SELECT chat_timestamp FROM {self.chat_table_name} WHERE chat_id = ?
                '''
                cursor.execute(timestamp_query, (last_row_id,))
                created_at = cursor.fetchone()["chat_timestamp"]
                conn.commit()

                # Return the ChatMessage with the timestamp
                return ChatMessage(last_row_id, from_user.id, to_user.id if to_user else -1, message, message_type, created_at)

        except sqlite3.IntegrityError as e:
            raise DBError("Failed to save chat message due to database integrity error.") from e

    def load_chat_messages(self, user: UserContainer) -> List[ChatMessage]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'''
                SELECT * FROM {self.chat_table_name} 
                WHERE (sender_id = ? AND to_id = -1) 
                OR (sender_id = -1 AND to_id = ?)
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
        self.create_dummy_user()
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

    def create_dummy_user(self):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT OR IGNORE INTO {self.user_table_name} (user_id, user_email, user_username, user_password, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (-1,'joshpassmore@outlook.com', 'ChatBot', 'chatbot', 'bot'))
            conn.commit()

    def delete_chat_message(self, message_id: int):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            delete_query = f'DELETE FROM {self.chat_table_name} WHERE chat_id = ?'
            cursor.execute(delete_query, (message_id,))
            conn.commit()

    def shutdown_controller(self, testing=False):
        if testing:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # Drop the user table
                    cursor.execute(f'DROP TABLE IF EXISTS {self.chat_table_name}')
                    conn.commit()
                except sqlite3.Error as e:
                    raise DBError(f"Failed to drop table {self.chat_table_name}: {e}")
