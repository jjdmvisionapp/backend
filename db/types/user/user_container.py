from dataclasses import dataclass


@dataclass
class UserContainer(frozen=True):
    id: int