import json
import secrets

from cachelib import FileSystemCache
from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.exceptions.db_error import DBError
from routes.user import create_user_blueprint


def create_app():

    # Create the app instance
    flask_app = Flask(__name__)
    print(flask_app.root_path)
    flask_app.config.from_file("config.json", load=json.load)

    debug = flask_app.config["DEBUG"]
    flask_app.config["SECRET_KEY"] = secrets.token_hex(16)
    flask_app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir='flask_session', threshold=500)
    flask_app.config["SESSION_TYPE"] = "cachelib"
    endpoint = flask_app.config["ENDPOINT"]
    Session(flask_app)
    CORS(flask_app)

    flask_app.register_blueprint(create_user_blueprint(endpoint))

    @flask_app.errorhandler(InvalidData)
    def handle_invalid_data(exception):
        if debug: flask_app.logger.exception(exception)
        message = {
            "status": "error",
            "message": "Invalid data provided",
        }
        return jsonify(message), 400

    @flask_app.errorhandler(DBError)
    def handle_db_error(exception):
        if debug: flask_app.logger.exception(exception)
        message = {
            "status": "error",
            "message": "Internal server error",
        }
        return jsonify(message), 500

    @flask_app.teardown_appcontext
    def shutdown_session(exc=None):
        DataResourceManager.shutdown()

    return flask_app


if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run(port=jjdm.config["PORT"])