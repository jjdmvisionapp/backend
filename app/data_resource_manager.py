import threading

from flask import Flask

from db.debug.cache_user_controller import CacheUserController
from db.sqlite.sqlite_db_adapter import SQLiteDBAdapter
from db.sqlite.user.sqlite3_user_controller import SQLite3UserController
from db.user_data_controller import UserDataController


# Quite a hacky method to get stuff passed around the app safely
class DataResourceManager:

    # Don't access this directly
    _user_data_controller = None
    _lock = threading.Lock()

    @staticmethod
    def get_user_data_controller(flask_app: Flask) -> UserDataController:
        if DataResourceManager._user_data_controller is None:
            with DataResourceManager._lock:  # Ensure thread-safe initialization
                if DataResourceManager._user_data_controller is None:
                    DataResourceManager._user_data_controller = _make_user_controller(flask_app)
        return DataResourceManager._user_data_controller

    @staticmethod
    def shutdown():
        with DataResourceManager._lock:
            if DataResourceManager._user_data_controller is not None:
                DataResourceManager._user_data_controller.shutdown()

def _make_user_controller(app: Flask) -> UserDataController:
    active_db = app.config["database"]["active"]
    if active_db == "sqlite":
        adaptor = SQLiteDBAdapter(app.config["database"]["sqlite"]["db_filename"],
                                  app.config["database"]["users_table_name"],
                                  app.config["database"]["chat_table_name"])
        return SQLite3UserController(

        )
    elif active_db == "cache":
        return CacheUserController()
    else:
        raise ValueError(f"Unsupported database type: {active_db}")
