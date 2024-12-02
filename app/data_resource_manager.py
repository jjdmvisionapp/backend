import os
import threading
from pathlib import Path

from flask import Flask

from db.chat_data_controller import ChatDataController
from db.image_data_controller import ImageDataController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.sqlite.user.sqlite3_user_controller import SQLite3UserController
from db.sqlite.chat.sqlite3_chat_controller import SQLite3ChatController
from db.sqlite.image.sqlite3_image_controller import SQLite3ImageController
from db.user_data_controller import UserDataController


# ChatGPT simplified
class DataResourceManager:

    _db_adaptor = None
    _user_data_controller = None
    _chat_data_controller = None
    _image_data_controller = None
    _lock = threading.Lock()

    @staticmethod
    def get_user_data_controller(flask_app: Flask) -> UserDataController:
        return DataResourceManager._get_data_controller(flask_app, 'user')

    @staticmethod
    def get_chat_data_controller(flask_app: Flask) -> ChatDataController:
        return DataResourceManager._get_data_controller(flask_app, 'chat')

    @staticmethod
    def get_image_data_controller(flask_app: Flask) -> ImageDataController:
        return DataResourceManager._get_data_controller(flask_app, 'image')

    @staticmethod
    def shutdown():
        with DataResourceManager._lock:
            if DataResourceManager._user_data_controller:
                DataResourceManager._user_data_controller.shutdown()
            if DataResourceManager._chat_data_controller:
                DataResourceManager._chat_data_controller.shutdown()
            if DataResourceManager._image_data_controller:
                DataResourceManager._image_data_controller.shutdown()

    @staticmethod
    def _set_db_adaptor(app: Flask):
        if DataResourceManager._db_adaptor is None:
            active_db = app.config["database"]["active"]
            if active_db == "sqlite":
                db_config = app.config["database"]["sqlite"]
                DataResourceManager._db_adaptor = SQLiteDBAdaptor(
                    db_filename=db_config["db_filename"],
                    user_table_name=app.config["database"]["users_table_name"],
                    chat_table_name=app.config["database"]["chat_table_name"],
                    image_table_name=app.config["database"]["image_table_name"]
                )
            else:
                raise ValueError(f"Unsupported database adaptor: {active_db}")

    @staticmethod
    def _get_data_controller(app: Flask, controller_type: str):
        with DataResourceManager._lock:
            if DataResourceManager._db_adaptor is None:
                DataResourceManager._set_db_adaptor(app)
            if controller_type == 'user' and DataResourceManager._user_data_controller is None:
                DataResourceManager._user_data_controller = SQLite3UserController(DataResourceManager._db_adaptor)
            elif controller_type == 'chat' and DataResourceManager._chat_data_controller is None:
                DataResourceManager._chat_data_controller = SQLite3ChatController(DataResourceManager._db_adaptor)
            elif controller_type == 'image' and DataResourceManager._image_data_controller is None:
                path = Path(app.root_path) / Path(app.config["modules"]["image_upload"]["upload_directory"])
                DataResourceManager._image_data_controller = SQLite3ImageController(DataResourceManager._db_adaptor, path)
            return {
                'user': DataResourceManager._user_data_controller,
                'chat': DataResourceManager._chat_data_controller,
                'image': DataResourceManager._image_data_controller
            }[controller_type]
