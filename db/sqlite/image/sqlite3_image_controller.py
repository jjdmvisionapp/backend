import sqlite3
from pathlib import Path
from typing import Optional

from classifiers.image_classifier import ImageClassifier
from db.image_data_controller import ImageDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.types.exceptions.db_error import DBError
from db.types.image import Image
from db.types.user.user_container import UserContainer


class SQLite3ImageController(ImageDataController):

    def __init__(self, sqlite_adaptor: SQLiteDBAdaptor, image_folder_path: Path, classifier: ImageClassifier):
        super().__init__(sqlite_adaptor, image_folder_path, classifier)
        self.image_folder_path = image_folder_path
        self.image_table_name = sqlite_adaptor.image_table_name
        self.user_table_name = sqlite_adaptor.user_table_name

    def init_controller(self):
        super().init_controller()
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.image_table_name} (
                    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name INTEGER,
                    image_width INTEGER,
                    image_height INTEGER,
                    image_hash TEXT UNIQUE,
                    image_mime TEXT,
                    user_id INTEGER,
                    classified_as TEXT,  -- New column for classification category
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- New timestamp column
                    FOREIGN KEY (user_id) REFERENCES {self.user_table_name}(user_id)
                    ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def _save_image_to_db(self, image_filename, image_width, image_height, image_hash, image_mime, user: UserContainer) -> Image:
        try:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()

                # Check if a row for this user already exists
                query_check = f'''
                    SELECT image_id FROM {self.image_table_name} WHERE user_id = ? AND image_hash = ?
                '''
                cursor.execute(query_check, (user.id, image_hash))
                row = cursor.fetchone()
                unique = row is None

                if not unique:
                    # Update the existing row
                    self._update_image_basics(cursor, image_filename, image_width, image_height, image_hash, image_mime, user.id)
                    image_id = row[0]  # Retrieve the ID of the existing image
                else:
                    # Insert a new row
                    query_insert = f'''
                        INSERT INTO {self.image_table_name} 
                        (image_name, image_width, image_height, image_hash, image_mime, classified_as, user_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    '''
                    cursor.execute(query_insert, (image_filename, image_width, image_height, image_hash, image_mime, None, user.id))
                    image_id = cursor.lastrowid

                conn.commit()
                return Image(image_id, image_filename, image_width, image_height, image_mime, image_hash, unique)

        except sqlite3.IntegrityError as e:
            # Handle database integrity errors if needed
            image_id = None  # Assign a default or error value
            return Image(image_id, image_filename, image_width, image_height, image_mime, None, False)

    def _update_image_basics(self, cursor, image_filename, image_width, image_height, image_hash, image_mime, user_id):
        query_update = f'''
            UPDATE {self.image_table_name}
            SET 
                image_name = ?, 
                image_width = ?, 
                image_height = ?, 
                image_hash = ?, 
                image_mime = ?
            WHERE user_id = ?
        '''
        cursor.execute(query_update, (image_filename, image_width, image_height, image_hash, image_mime, user_id))

    def _update_classified_as(self, image_id, classified_as):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'UPDATE {self.image_table_name} SET classified_as = ? WHERE image_id = ?'
            cursor.execute(query, (classified_as, image_id))
            conn.commit()
            return cursor.rowcount > 0  # Returns True if a row was updated

    def _update_image_db(self, image_id, image_filename, image_width, image_height, image_hash, image_mime, user_id) -> Optional[str]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            self._update_image_basics(cursor, image_filename, image_width, image_height, image_hash, image_mime, user_id)
        return True

    def _get_image_from_db(self, user: UserContainer) -> Optional[Image]:
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            query = f'SELECT * FROM {self.image_table_name} WHERE user_id = ? ORDER BY created_at DESC LIMIT 1'
            row = cursor.execute(query, (user.id,)).fetchone()
            conn.commit()
            if row is None:  # Check if no result was returned
                return None  # Return None or handle this case as needed
            return Image(row["IMAGE_ID"], row["IMAGE_NAME"], row["IMAGE_WIDTH"], row["IMAGE_HEIGHT"], row["IMAGE_MIME"], row["CLASSIFIED_AS"])

    def delete_image(self, image_id: int):
        with self.db_adaptor.get_connection() as conn:
            cursor = conn.cursor()
            user_query = f'DELETE FROM {self.image_table_name} WHERE image_id = ?'
            cursor.execute(user_query, (image_id,))
            conn.commit()

    def shutdown_controller(self, testing=False):
        if testing:
            with self.db_adaptor.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # Drop the user table
                    cursor.execute(f'DROP TABLE IF EXISTS {self.image_table_name}')
                    conn.commit()
                except sqlite3.Error as e:
                    raise DBError(f"Failed to drop table {self.image_table_name}: {e}")
