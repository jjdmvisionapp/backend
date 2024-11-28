from abc import abstractmethod

from db.data_controller import DataController


class ChatDataController(DataController):

    @abstractmethod
    def send_chat_message(self, from_user, to_user, message):
        pass