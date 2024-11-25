import json

from flask import Flask
from flask_session import Session

from db.debug.cache_user_controller import CacheUserController
from db.sqlite.sqlite3_user_controller import SQLite3UserController


def create_app():

    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    Session(app)

    active_db = app.config["database"]["active"]

    if active_db == "sqlite":
        app.user_controller = SQLite3UserController(
            app.config["database"]["sqlite"]["db_filename"],
            app.config["database"]["users_table_name"]
        )
    else:
        app.user_controller = CacheUserController()

    return app

if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run()