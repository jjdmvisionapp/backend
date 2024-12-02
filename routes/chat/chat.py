from flask import Blueprint, request, current_app, session, jsonify

from app.data_resource_manager import DataResourceManager
from db.types.user.user_container import UserContainer
from routes.util import login_required

chat_blueprint = Blueprint('user', __name__, url_prefix=current_app.config["endpoint"] + '/chat')

@login_required
@chat_blueprint.route("/messages", methods=["GET"])
def messages():
    if request.method == "GET":
        chat_controller = DataResourceManager.get_chat_data_controller(current_app)
        user = UserContainer(session['user_id'])

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




