import json
from dataclasses import dataclass

@dataclass
class User(frozen=True):
    id: int
    username: str
    email: str
    # hashed
    password: str
    type: str
