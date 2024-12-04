from abc import ABC, abstractmethod


class ChatBotController(ABC):
    @abstractmethod
    def ask_chatbot(self, message) -> str:
        pass