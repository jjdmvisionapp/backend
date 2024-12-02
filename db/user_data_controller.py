import json
from abc import abstractmethod
from typing import List, Optional

from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash

from app.exceptions.invalid_data import InvalidData
from db.data_controller import DataController
from db.types.user.user_container import UserContainer
from types.user import User


def user_to_dict(user: User):
    return {
        'id': user.id,
        'username': user.username,
    }

class UserDataController(DataController):

    def create_new_user(self, username: str, email: str, password: str) -> UserContainer:
        try:
            valid = validate_email(email)
            email = valid.normalized_email
            hashed_password = generate_password_hash(password)
            return self._create_user_impl(username, email, hashed_password)
        except EmailNotValidError as e:
            raise InvalidData

    @abstractmethod
    def _create_user_impl(self, username: str, email: str, password: str, user_type: str) -> UserContainer:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[UserContainer]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[UserContainer]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserContainer]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserContainer]:
        pass

    @abstractmethod
    def delete_user(self, user: UserContainer):
        pass

    @abstractmethod
    def shutdown_controller(self):
        pass

    def json_to_user(self, json_str: str) -> Optional[UserContainer]:
        to_load = json.loads(json_str)
        return self.get_user_by_id(to_load['id'])

