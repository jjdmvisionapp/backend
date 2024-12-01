# User controller specifically for the sqlite dialect of SQL.
import sqlite3
from typing import List, Optional

from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.exceptions.db_error import DBError
from db.types.user import User
from db.user_data_controller import UserDataController


# User controller specifically for the sqlite dialect of SQL.
class SQLite3UserController(UserDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor):
        super().__init__(sqlite_adaptor)
        self.user_table_name = sqlite_adaptor.user_table_name

    def _get_user_by_attrib(self, column_name: str, value: str) -> Optional[User]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name} WHERE {column_name} = ?'
            row = cursor.execute(query, (value.lower(),)).fetchone()
            if row:
                return User(
                    id=row['user_id'],
                    username=row['user_username'],
                    email=row['user_email'],
                    password=row['user_password'],
                    type=row['user_type']  # Simply return the string value from the database
                )
            return None

    def init_controller(self):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            # User Table (stores user info)
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.user_table_name} (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_username TEXT NOT NULL UNIQUE,
                    user_email TEXT NOT NULL UNIQUE,
                    user_password TEXT NOT NULL,
                    user_type TEXT NOT NULL
                )
            ''')
            conn.commit()

    def _create_user_impl(self, username: str, email: str, password: str, user_type: str) -> User:
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                query = f'''
                    INSERT INTO {self.user_table_name} 
                    (user_username, user_email, user_password, user_type) 
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(query, (username.lower(), email.lower(), password, user_type.lower()))
                conn.commit()
                last_inserted_id = cursor.lastrowid
                return User(last_inserted_id, username.lower(), email.lower(), password, user_type.lower())
        except sqlite3.IntegrityError as e:
            raise DBError("User with this username or email already exists.") from e

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._get_user_by_attrib("user_username", username)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name} WHERE user_id = ?'
            row = cursor.execute(query, (user_id,)).fetchone()
            if row:
                return User(
                    id=row['user_id'],
                    username=row['user_username'],
                    email=row['user_email'],
                    password=row['user_password'],
                    type=row['user_type']  # Return string value of user_type
                )
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self._get_user_by_attrib("user_email", email)

    def get_all_users(self) -> List[User]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name}'
            rows = cursor.execute(query).fetchall()
            return [
                User(
                    id=row['user_id'],
                    username=row['user_username'],
                    email=row['user_email'],
                    password=row['user_password'],
                    type=row['user_type']  # Return the user type as a string
                )
                for row in rows
            ]

    def delete_user(self, user_id: int):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            user_query = f'DELETE FROM {self.user_table_name} WHERE user_id = ?'
            cursor.execute(user_query, (user_id,))
            conn.commit()

    def shutdown_controller(self):
        pass

