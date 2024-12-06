import json
import secrets
import threading

import socketio
from cachelib import FileSystemCache
from flask import Flask, jsonify, request, Response, session, g
from flask_cors import CORS
from flask_session import Session
from flask_socketio import disconnect, emit, SocketIO

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.exceptions.db_error import DBError
from routes.chat import create_chat_blueprint
from routes.images import create_images_blueprint
from routes.user import create_user_blueprint


def create_app(testing=False):
    from app.data_resource_manager import DataResourceManager
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
            res.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
            res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            res.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            res.headers["Access-Control-Allow-Credentials"] = "true"
            return res

    @flask_app.teardown_appcontext
    def shutdown_session(exc=None):
        DataResourceManager.shutdown(testing)

    socket = SocketIO(flask_app, cors_allowed_origins="*", manage_session=False)

    # # Event handler for connection
    # @socket.on('connect', namespace='/chat')
    # def handle_connect():
    #     user_id = g.get("USER_ID")
    #     if not user_id:
    #         disconnect()  # Disconnect the user if not authenticated
    #     else:
    #         emit('response', {'status': 'success', 'message': 'User authenticated'})

    @socket.on('send_message', namespace='/chat')
    def handle_message(data):
        print(data)
        returned_json, from_user_id, to_user = DataResourceManager.get_chat_callback(data)
        print(returned_json, from_user_id, to_user)
        emit('receive_message', returned_json, to=str(from_user_id), namespace='/chat')

    # Run SocketIO in a separate thread
    def run_socket():
        socket.run(flask_app, port=flask_app.config["MODULES"]["CHATBOT"]["PORT"])

    threading.Thread(target=run_socket, daemon=True).start()

    return flask_app


if __name__ == '__main__':
    jjdm = create_app()
    jjdm.run(port=jjdm.config["PORT"])
