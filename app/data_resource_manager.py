import threading
from pathlib import Path
from typing import Callable, Tuple, Dict

from flask import Flask

from chatbots.huggingface.flan_t5_chatbot import FlanT5ChatBot
from classifiers.resnet import ResNetClassifier
from db.chat_data_controller import ChatDataController
from db.image_data_controller import ImageDataController
from db.sqlite.chat.sqlite3_chat_controller import SQLite3ChatController
from db.sqlite.image.sqlite3_image_controller import SQLite3ImageController
from db.sqlite.sqlite_db_adaptor import SQLiteDBAdaptor
from db.sqlite.user.sqlite3_user_controller import SQLite3UserController
from db.user_data_controller import UserDataController


def _chatbot_not_ready(json: Dict[str, str]) -> Tuple[Dict[str, str], int, int]:
    return {
        "error": "Chatbot is not ready yet!"
    }, -1, -1


# ChatGPT simplified
class DataResourceManager:
    _db_adaptor = None
    _user_data_controller = None
    _chat_data_controller = None
    _image_data_controller = None
    _socket = None
    _lock = threading.Lock()

    _chat_callback = _chatbot_not_ready

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
    def change_chat_callback(function: Callable[[Dict[str, str]], Tuple[Dict[str, str], int, int]]):
        DataResourceManager._chat_callback = function

    @staticmethod
    def get_chat_callback(json: Dict[str, str]) -> Tuple[Dict[str, str], int, int]:
        return DataResourceManager._chat_callback(json)

    @staticmethod
    def shutdown(testing=False):
        with DataResourceManager._lock:
            if DataResourceManager._user_data_controller:
                DataResourceManager._user_data_controller.shutdown_controller(testing)
            if DataResourceManager._chat_data_controller:
                DataResourceManager._chat_data_controller.shutdown_controller(testing)
            if DataResourceManager._image_data_controller:
                DataResourceManager._image_data_controller.shutdown_controller(testing)

    @staticmethod
    def _set_db_adaptor(app: Flask):
        if DataResourceManager._db_adaptor is None:
            db = app.config["DATABASE"]
            active_db = db["ACTIVE"]
            if active_db == "sqlite":
                db_config = db["SQLITE"]
                DataResourceManager._db_adaptor = SQLiteDBAdaptor(
                    db_filename=db_config["DB_FILENAME"],
                    user_table_name=db["USERS_TABLE_NAME"],
                    chat_table_name=db["CHAT_TABLE_NAME"],
                    image_table_name=db["IMAGES_TABLE_NAME"]
                )
            else:
                raise ValueError(f"Unsupported database adaptor: {active_db}")

    @staticmethod
    def _get_data_controller(app: Flask, controller_type: str):
        with DataResourceManager._lock:
            if DataResourceManager._db_adaptor is None:
                DataResourceManager._set_db_adaptor(app)
            if controller_type == 'user' and DataResourceManager._user_data_controller is None:
                user_controller = SQLite3UserController(DataResourceManager._db_adaptor)
                user_controller.init_controller()
                DataResourceManager._user_data_controller = user_controller
            elif controller_type == 'chat' and DataResourceManager._chat_data_controller is None:
                chatbot = FlanT5ChatBot(app)
                chat_controller = SQLite3ChatController(DataResourceManager._db_adaptor, chatbot)
                chat_controller.init_controller()
                DataResourceManager._chat_data_controller = chat_controller
            elif controller_type == 'image' and DataResourceManager._image_data_controller is None:
                image_upload_directory = Path(app.root_path) / Path(app.config["MODULES"]["IMAGE_UPLOAD"]["UPLOAD_DIRECTORY"])
                classes_path = Path(app.root_path) / "imagenet_classes.txt"
                image_controller = SQLite3ImageController(DataResourceManager._db_adaptor, image_upload_directory, ResNetClassifier(class_file=classes_path))
                image_controller.init_controller()
                DataResourceManager._image_data_controller = image_controller
            return {
                'user': DataResourceManager._user_data_controller,
                'chat': DataResourceManager._chat_data_controller,
                'image': DataResourceManager._image_data_controller
            }[controller_type]
