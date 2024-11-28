from abc import abstractmethod

from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.user import User


class ChatDataController(DataController):

    @abstractmethod
    def _save_chat_message_impl(self, from_user: User, to_user: User, message: str):
        pass



