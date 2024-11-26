import json
from abc import abstractmethod
from typing import List, Optional

from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash

from app.exceptions.invalid_data import InvalidData
from db.db_adapter import DBAdaptor
from types.user import User


def user_to_dict(user: User):
    return {
        'id': user.id,
        'username': user.username,
    }

class UserDataController:

    def __init__(self, db_adaptor: DBAdaptor):
        self.db_adaptor = db_adaptor

    @abstractmethod
    def init_controller(self):
        pass

    def create_new_user(self, username: str, email: str, password: str) -> User:
        try:
            valid = validate_email(email)
            email = valid.normalized_email
            hashed_password = generate_password_hash(password)
            return self._create_user_impl(username, email, hashed_password)
        except EmailNotValidError as e:
            raise InvalidData

    @abstractmethod
    def _create_user_impl(self, username: str, email: str, password: str) -> User:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def shutdown_controller(self):
        pass

    def json_to_user(self, json_str: str) -> Optional[User]:
        to_load = json.loads(json_str)
        return self.get_user_by_id(to_load['id'])

