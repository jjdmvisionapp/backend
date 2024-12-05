import json
from abc import abstractmethod
from typing import List, Optional

from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash

from app.exceptions.invalid_data import InvalidData
from db.data_controller import DataController
from db.types.user.complete_user import CompleteUser
from db.types.user.user_container import UserContainer


def user_to_dict(user: CompleteUser) -> dict:
    return {
        'id': user.id,
        'username': user.username,
    }

class UserDataController(DataController):

    def create_new_user(self, username: str, email: str, password: str, user_type: str) -> CompleteUser:
        try:
            valid = validate_email(email)
            email = valid.normalized
            hashed_password = generate_password_hash(password)
            return self._create_user_impl(username, email, hashed_password, user_type)
        except EmailNotValidError:
            raise InvalidData("Email not valid")

    @abstractmethod
    def _create_user_impl(self, username: str, email: str, password: str, user_type: str) -> CompleteUser:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[CompleteUser]:
        pass

    def validate_user(self, username: str, given_password: str, given_email: str) -> Optional[CompleteUser]:
        user = self.get_user_by_username(username)
        if user is not None:
            if check_password_hash(user.password, given_password) and given_email == user.email:
                return user
        return None

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[CompleteUser]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[CompleteUser]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserContainer]:
        pass

    @abstractmethod
    def delete_user(self, user: UserContainer):
        pass

    @abstractmethod
    def update_user(self, user_id: int, attribute: str, new_value):
        pass

    @abstractmethod
    def shutdown_controller(self, testing=False):
        pass

    def json_to_user(self, json_str: str) -> Optional[UserContainer]:
        to_load = json.loads(json_str)
        return self.get_user_by_id(to_load['id'])

