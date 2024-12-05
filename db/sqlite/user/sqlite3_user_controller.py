# User controller specifically for the sqlite dialect of SQL.
import sqlite3
from typing import List, Optional

from app.exceptions.invalid_data import InvalidData
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.exceptions.db_error import DBError
from db.types.user.complete_user import CompleteUser
from db.types.user.user_container import UserContainer
from db.user_data_controller import UserDataController


# User controller specifically for the sqlite dialect of SQL.
class SQLite3UserController(UserDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor):
        super().__init__(sqlite_adaptor)
        self.user_table_name = sqlite_adaptor.user_table_name

    def _get_user_by_attrib(self, column_name: str, value) -> Optional[CompleteUser]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name} WHERE {column_name} = ?'
            row = cursor.execute(query, (value,)).fetchone()
            if row:
                return CompleteUser(
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
            print("called init")

    def _create_user_impl(self, username: str, email: str, password: str, user_type: str) -> UserContainer:
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
                return CompleteUser(last_inserted_id, username.lower(), email.lower(), password, user_type.lower())
        except sqlite3.IntegrityError:
            raise InvalidData("User already exists")

    def get_user_by_username(self, username: str) -> Optional[CompleteUser]:
        return self._get_user_by_attrib("user_username", username.lower())

    def get_user_by_id(self, user_id: int) -> Optional[UserContainer]:
        return self._get_user_by_attrib("user_id", user_id)

    def get_user_by_email(self, email: str) -> Optional[UserContainer]:
        return self._get_user_by_attrib("user_email", email.lower())

    def get_all_users(self) -> List[UserContainer]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.user_table_name}'
            rows = cursor.execute(query).fetchall()
            return [
                CompleteUser(
                    id=row['user_id'],
                    username=row['user_username'],
                    email=row['user_email'],
                    password=row['user_password'],
                    type=row['user_type']  # Return the user type as a string
                )
                for row in rows
            ]

    def delete_user(self, user: UserContainer):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            user_query = f'DELETE FROM {self.user_table_name} WHERE user_id = ?'
            cursor.execute(user_query, (user.id,))
            conn.commit()


    # ChatGPT partially
    def update_user(self, user_id: int, attribute: str, new_value):
        # Validate the column name to prevent SQL injection
        column = f'user_{attribute}'
        valid_columns = {"user_username", "user_email", "user_password", "user_type"}
        if column not in valid_columns:
            raise DBError(f"Invalid column name: {column}")
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                query = f'UPDATE {self.user_table_name} SET {column} = ? WHERE user_id = ?'
                cursor.execute(query, (new_value, user_id))
                if cursor.rowcount == 0:
                    raise DBError(f"No user found with ID {user_id}.")
                conn.commit()
        except sqlite3.IntegrityError as e:
            raise DBError("Error updating user. This might be due to a unique constraint violation.") from e

    def shutdown_controller(self, testing=False):
        if testing:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # Drop the user table
                    cursor.execute(f'DROP TABLE IF EXISTS {self.user_table_name}')
                    conn.commit()
                except sqlite3.Error as e:
                    raise DBError(f"Failed to drop table {self.user_table_name}: {e}")



