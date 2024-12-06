import json
import secrets

import socketio
from cachelib import FileSystemCache
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_session import Session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.exceptions.db_error import DBError
from routes.chat import create_chat_blueprint
from routes.images import create_images_blueprint
from routes.user import create_user_blueprint


def create_app(testing=False):

    # Create the app instance
    flask_app = Flask(__name__)
    flask_app.config.from_file("config.json", load=json.load)

    flask_app.config["SECRET_KEY"] = secrets.token_hex(16)
    flask_app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir='sessions', threshold=500)
    flask_app.config["SESSION_TYPE"] = "cachelib"
    flask_app.config['SESSION_PERMANENT'] = True
    endpoint = flask_app.config["ENDPOINT"]
    Session(flask_app)
    CORS(flask_app, supports_credentials=True)

    flask_app.register_blueprint(create_user_blueprint(endpoint))
    flask_app.register_blueprint(create_images_blueprint(endpoint))
    flask_app.register_blueprint(create_chat_blueprint(endpoint))

    @flask_app.errorhandler(InvalidData)
    def handle_invalid_data(exception):
        if testing: flask_app.logger.exception(exception)
        message = {
            "status": "error",
            "message": "Invalid data provided",
        }
        return jsonify(message), 400

    @flask_app.errorhandler(DBError)
    def handle_db_error(exception):
        if testing: flask_app.logger.exception(exception)
        message = {
            "status": "error",
            "message": "Internal server error",
        }
        return jsonify(message), 500

    @flask_app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            res = Response()
            res.headers['X-Content-Type-Options'] = '*'
            return res

    @flask_app.teardown_appcontext
    def shutdown_session(exc=None):
        DataResourceManager.shutdown(testing)


    return flask_app


if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run(port=jjdm.config["PORT"])