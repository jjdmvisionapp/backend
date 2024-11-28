from abc import abstractmethod

from flask import current_app
from flask_socketio import SocketIO

from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.user import User


# TODO: Maybe move socket io functions to a separate class
class ChatDataController(DataController):

    def __init__(self, db_adaptor: DBAdaptor):
        super().__init__(db_adaptor)

    def init_controller(self):
        socket = SocketIO(current_app, cors_allowed_origins="*")
        @socket.on('message', namespace='/chat')
        def handle_message(json):
            pass

    @abstractmethod
    def _ask_chatbot(self, message):
        pass

    def send_message(self, from_user: User, to_user: User, message: str):
        pass

    @abstractmethod
    def load_chat_messages(self, user: User):
        pass

    @abstractmethod
    def _save_chat_message_impl(self, from_user: User, to_user: User, message: str):
        pass



