import sqlite3
from pathlib import Path
from typing import Optional

from db.image_data_controller import ImageDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.exceptions.db_error import DBError
from db.types.image import Image
from db.types.user.user_container import UserContainer


class SQLite3ImageController(ImageDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor, image_folder_path: Path):
        super().__init__(sqlite_adaptor, image_folder_path)
        self.image_folder_path = image_folder_path
        self.image_table_name = sqlite_adaptor.image_table_name
        self.user_table_name = sqlite_adaptor.user_table_name

    def init_controller(self):
        super().init_controller()
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            # User Table (stores user info)
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.image_table_name} (
                    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name INTEGER,
                    image_width INTEGER,
                    image_height INTEGER,
                    user_id INTEGER,
                    FOREIGN KEY (sender_id) REFERENCES {self.user_table_name}(user_id)
                    ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def _save_image_to_db(self, image_filename, image_width, image_height, user: UserContainer) -> Image:
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                query = f'''
                    INSERT INTO {self.image_table_name} 
                    (image_name, image_width, image_height, user_id) 
                    VALUES (?, ?, ?, ?)
                '''
                cursor.execute(query, (image_filename, image_width, image_height, user.id))
                conn.commit()
                return Image(cursor.lastrowid, image_filename, image_width, image_height)
        except sqlite3.IntegrityError as e:
            raise DBError("User with this username or email already exists.") from e

    def get_image_from_db(self, user: UserContainer) -> Optional[Image]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.image_table_name} WHERE user_id = ?'
            row = cursor.execute(query, (user.id,)).fetchone()
            conn.commit()
            if row is None:  # Check if no result was returned
                return None  # Return None or handle this case as needed
            return Image(row["image_id"], row["image_name"], row["image_width"], row["image_height"])

    def delete_image(self, image_id: int):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            user_query = f'DELETE FROM {self.image_table_name} WHERE image_id = ?'
            cursor.execute(user_query, (image_id,))
            conn.commit()