from abc import abstractmethod, ABC
from typing import List

from flask import current_app, session
from flask_socketio import SocketIO, emit, disconnect

from chatbots.chatbot_controller import ChatBotController
from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.chat_message import ChatMessage

from db.types.user.user_container import UserContainer



def _run_chatbot(socket: SocketIO):
    with current_app.app_context():
        port = current_app.config["MODULES"]["CHATBOT"]["PORT"]
        socket.run(port=port, app=current_app)


class ChatDataController(DataController, ABC):

    CHATBOT_ID = -1

    def __init__(self, db_adaptor: DBAdaptor, chatbot: ChatBotController):
        super().__init__(db_adaptor)
        self.chatbot_controller = chatbot

    def init_controller(self):
        socket = SocketIO(current_app, cors_allowed_origins="*")

        # Event handler for connection
        @socket.on('connect', namespace='/chat')
        def handle_connect():
            if "username" not in session or "email" not in session:
                disconnect()  # Disconnect the user if not authenticated
            else:
                emit('response', {'status': 'success', 'message': 'User authenticated'})

        @socket.on('send_message', namespace='/chat')
        def handle_message(data):

            try:
                # Extract data from the incoming WebSocket message
                message = data.get('message')
                from_user_id = data.get('from_user_id')
                to_user_id = data.get('to_user_id', self.CHATBOT_ID)  # Default to the chatbot

                # Fetch the sender's information
                chatbot = UserContainer(to_user_id)
                user = UserContainer(from_user_id)

                if to_user_id == self.CHATBOT_ID:
                    # Message to the chatbot
                    chatbot_response = self.chatbot_controller.ask_chatbot(message)

                    # Save the user's message and chatbot's response in the database
                    user_message = self._save_chat_message_impl(chatbot, user, message, 'user')
                    bot_message = self._save_chat_message_impl(user, chatbot, chatbot_response, 'bot')

                    # Emit both messages back to the sender
                    emit('receive_message', user_message.to_dict(), to=from_user_id, namespace='/chat')
                    emit('receive_message', bot_message.to_dict(), to=from_user_id, namespace='/chat')

                else:
                    # Message to another user
                    to_user = UserContainer(to_user_id)
                    chat_message = self._save_chat_message_impl(chatbot, to_user, message, 'user')

                    # Emit the message to both sender and recipient
                    emit('receive_message', chat_message.to_dict(), to=from_user_id, namespace='/chat')
                    emit('receive_message', chat_message.to_dict(), to=to_user_id, namespace='/chat')

            except Exception as e:
                emit('error', {'error': str(e)}, namespace='/chat')

            _run_chatbot(socket)


    # def send_message(self, from_user: User, to_user: User, message: str):
    #     pass

    @abstractmethod
    def load_chat_messages(self, user: UserContainer) -> List[ChatMessage]:
        pass

    @abstractmethod
    def _save_chat_message_impl(self, from_user: UserContainer, to_user: UserContainer, message: str, message_type: str) -> ChatMessage:
        pass

    @abstractmethod
    def delete_chat_message(self, user: UserContainer):
        pass



