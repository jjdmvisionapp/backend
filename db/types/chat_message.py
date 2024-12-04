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
    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "type": self.type,
            "timestamp": self.timestamp,
        }
