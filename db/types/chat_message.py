from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    message_id: int
    sender_id: int
    receiver_id: int
    message: str
    type: str
    timestamp: datetime