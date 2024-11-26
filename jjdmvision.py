import json

from flask import Flask, current_app, g
from flask_session import Session
from werkzeug.local import LocalProxy

from db.debug.cache_user_controller import CacheUserController
from db.sqlite.sqlite3_user_controller import SQLite3UserController
from db.user_data_controller import UserDataController
from routes.user.user import user_blueprint

def create_app():
    # Create the app instance
    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    Session(app)

    # Set up the user_controller based on the active database
    active_db = app.config["database"]["active"]

    user_controller = make_user_controller(app)

    app.register_blueprint(user_blueprint)

    return app

# Define the proxy for user_controller
def make_user_controller(app):
    active_db = app.config["database"]["active"]
    if active_db == "sqlite":
        return SQLite3UserController(
            app.config["database"]["sqlite"]["db_filename"],
            app.config["database"]["users_table_name"]
        )
    elif active_db == "cache":
        return CacheUserController()
    else:
        raise ValueError(f"Unsupported database type: {active_db}")

if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run()