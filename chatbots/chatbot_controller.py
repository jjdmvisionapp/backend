from abc import ABC, abstractmethod


class ChatBotController(ABC):
    @abstractmethod
    def _ask_chatbot(self, message) -> str:
        pass