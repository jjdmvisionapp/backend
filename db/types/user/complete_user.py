import json
from dataclasses import dataclass

from db.types.user.user_container import UserContainer


@dataclass
class CompleteUser(UserContainer, frozen=True):
    username: str
    email: str
    # hashed
    password: str
    type: str
