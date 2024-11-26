from db.debug.cache_user_controller import CacheUserController
from db.sqlite.user.sqlite3_user_controller import SQLite3UserController


# chatgpt lol
class UserControllerExtension:
    def __init__(self, app=None):
        self.user_controller = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        active_db = app.config["database"]["active"]
        if active_db == "sqlite":
            self.user_controller = SQLite3UserController(
                app.config["database"]["sqlite"]["db_filename"],
                app.config["database"]["users_table_name"]
            )
        else:
            self.user_controller = CacheUserController()
        app.user_controller = self.user_controller  # Optional, to keep global access
        app.extensions["user_controller"] = self  # Register in Flask extensions