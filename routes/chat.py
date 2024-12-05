from flask import Blueprint, request, current_app, jsonify

from app.data_resource_manager import DataResourceManager
from db.types.user.user_container import UserContainer
from routes.util import login_required


def create_chat_blueprint(blueprint):

    chat_blueprint = Blueprint('chat', __name__, url_prefix=blueprint + '/chat')

    @login_required
    @chat_blueprint.route("/messages", methods=["GET"])
    def messages(user_id):
        if request.method == "GET":
            chat_controller = DataResourceManager.get_chat_data_controller(current_app)
            user = UserContainer(user_id)

            # Load chat messages
            chat_messages = chat_controller.load_chat_messages(user)

            # Convert messages to dictionaries
            messages_dict = [
                {
                    "id": chat.message_id,
                    "sender_id": chat.sender_id,
                    "receiver_id": chat.receiver_id,
                    "content": chat.message,
                    "type": chat.type,
                    "timestamp": chat.timestamp.isoformat()  # Ensure timestamp is serialized
                }
                for chat in chat_messages
            ]

            # Return as JSON response
            return jsonify({"status": "success", "messages": messages_dict}), 200

    return chat_blueprint







