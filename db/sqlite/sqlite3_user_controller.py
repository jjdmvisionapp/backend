import sqlite3
from typing import List, Optional

from werkzeug.security import generate_password_hash

from db.types.exceptions.db_error import DBError
from db.types.user import User
from db.user_data_controller import UserDataController


class SQLite3UserController(UserDataController):

    def __init__(self, db_file_name: str, user_table_name: str):
        self.db_file_name = db_file_name
        self.user_table_name = user_table_name

    def _get_connection(self):
        conn = sqlite3.connect(self.db_file_name)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_user_by_attrib(self, column_name) -> Optional[User]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name} WHERE username = ?'
            row = cursor.execute(query, (column_name,)).fetchone()
            if row:
                return User(row['id'], row['username'], row['email'], row['password'])
            return None

    def init_controller(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.user_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

    def _create_user_impl(self, username: str, email: str, password: str) -> User:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f'INSERT INTO {self.user_table_name} (username, email, password) VALUES (?, ?, ?)'
                cursor.execute(query, (username, email, hashed_password))
                conn.commit()
                last_inserted_id = cursor.lastrowid
                return User(last_inserted_id, username, email, hashed_password)
        except sqlite3.IntegrityError as e:
            raise DBError("User with this email already exists.") from e

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._get_user_by_attrib('username')

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._get_user_by_attrib('id')

    def get_all_users(self) -> List[User]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name}'
            rows = cursor.execute(query).fetchall()
            return [User(row['id'], row['username'], row['email'], row['password']) for row in rows]

    def delete_user(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f'DELETE FROM {self.user_table_name} WHERE id = ?'
            cursor.execute(query, (user_id,))
            conn.commit()


    def shutdown_controller(self):
        pass
