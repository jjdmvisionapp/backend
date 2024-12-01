from dataclasses import dataclass

from db.types.user import User


@dataclass
class ChatMessage:
    message_id: int
    sender_id: int
    receiver_id: int
    message: str
    type: str