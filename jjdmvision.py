import json
import secrets

from flask import Flask, jsonify
from flask_session import Session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_user_input import InvalidUserInput
from db.types.exceptions.db_error import DBError
from routes.user.user import user_blueprint


def create_app():

    # Create the app instance
    flask_app = Flask(__name__)
    flask_app.config.from_file("config.json", load=json.load)

    debug = flask_app.config["debug"]
    flask_app.config["SECRET_KEY"] = secrets.token_hex(16)
    flask_app.config["SESSION_TYPE"] = "cachelib"
    Session(flask_app)

    flask_app.register_blueprint(user_blueprint)

    @flask_app.errorhandler(InvalidUserInput)
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
    def shutdown_session(exception=None):
        DataResourceManager.shutdown()

    return flask_app


if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run()