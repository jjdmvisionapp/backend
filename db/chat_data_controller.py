from abc import abstractmethod, ABC
from typing import List

from flask import current_app
from flask_socketio import SocketIO

from chatbots.chatbot_controller import ChatBotController
from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.chat_message import ChatMessage

from db.types.user.user_container import UserContainer


# TODO: Maybe move socket io functions to a separate class
class ChatDataController(DataController, ABC):

    def __init__(self, db_adaptor: DBAdaptor, chatbot: ChatBotController):
        super().__init__(db_adaptor)
        self.chatbot_controller = chatbot

    def init_controller(self):
        socket = SocketIO(current_app, cors_allowed_origins="*")
        @socket.on('message', namespace='/chat')
        def handle_message(json):
            pass

    # def send_message(self, from_user: User, to_user: User, message: str):
    #     pass

    @abstractmethod
    def load_chat_messages(self, user: UserContainer) -> List[ChatMessage]:
        pass

    @abstractmethod
    def _save_chat_message_impl(self, from_user: UserContainer, to_user: UserContainer, message: str):
        pass

    @abstractmethod
    def delete_chat_message(self, user: UserContainer):
        pass



