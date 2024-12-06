from abc import abstractmethod, ABC
from typing import List, Tuple, Dict, Any

from flask import current_app
from flask_socketio import emit
from chatbots.chatbot_controller import ChatBotController
from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.chat_message import ChatMessage
from db.types.user.user_container import UserContainer


class ChatDataController(DataController, ABC):

    CHATBOT_ID = -1

    def __init__(self, db_adaptor: DBAdaptor, chatbot: ChatBotController):
        super().__init__(db_adaptor)
        self.chatbot_controller = chatbot

    def chat_callback(self, data: Dict[str, Any]) -> Tuple[Dict[str, str], int, int]:
        """
        Processes incoming chat data and returns a tuple containing the message dictionary,
        the sender's user ID, and the recipient's user ID.
        """
        print("yo")
        try:
            # Extract data from the incoming WebSocket message
            message = data.get('message')
            from_user_id = data.get('from_user_id')
            to_user_id = data.get('to_user_id', self.CHATBOT_ID)  # Default to the chatbot

            # Validate required fields
            if not message or not from_user_id:
                raise ValueError("Message and from_user_id are required.")

            # Fetch the sender's information
            chatbot = UserContainer(self.CHATBOT_ID)
            user = UserContainer(from_user_id)

            if to_user_id == self.CHATBOT_ID:
                # Message to the chatbot
                chatbot_response = self.chatbot_controller.ask_chatbot(message)

                # Save the user's message and chatbot's response in the database
                user_message = self._save_chat_message_impl(chatbot, user, message, 'user')
                bot_message = self._save_chat_message_impl(user, chatbot, chatbot_response, 'bot')

                # Return the chatbot's response message
                return bot_message.to_dict(), from_user_id, self.CHATBOT_ID
            else:
                # Message to another user
                to_user = UserContainer(to_user_id)
                chat_message = self._save_chat_message_impl(user, to_user, message, 'user')

                # Return the message for delivery
                return chat_message.to_dict(), from_user_id, to_user_id

        except Exception as e:
            # Handle any exceptions by returning an error message
            error_message = {"status": "error", "message": str(e)}
            return error_message, -1, -1  # Use -1 as a placeholder for user IDs in case of error

    def init_controller(self):
        from app.data_resource_manager import DataResourceManager
        """
        Initialize the chat data controller and register its callback.
        """
        DataResourceManager.change_chat_callback(self.chat_callback)

    @abstractmethod
    def load_chat_messages(self, user: UserContainer) -> List[ChatMessage]:
        pass

    @abstractmethod
    def _save_chat_message_impl(self, from_user: UserContainer, to_user: UserContainer, message: str, message_type: str) -> ChatMessage:
        pass

    @abstractmethod
    def delete_chat_message(self, user: UserContainer):
        pass
