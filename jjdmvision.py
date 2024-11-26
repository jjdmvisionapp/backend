import json

from flask import Flask, current_app, g
from flask_session import Session
from werkzeug.local import LocalProxy

from app.data_resource_manager import DataResourceManager
from db.debug.cache_user_controller import CacheUserController
from db.sqlite.sqlite3_user_controller import SQLite3UserController
from db.user_data_controller import UserDataController
from routes.user.user import user_blueprint


def create_app():

    # Create the app instance
    flask_app = Flask(__name__)
    flask_app.config.from_file("config.json", load=json.load)
    Session(flask_app)

    flask_app.register_blueprint(user_blueprint)

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        DataResourceManager.shutdown()

    return flask_app


# Define the proxy for user_controller


if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run()