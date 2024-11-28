from typing import List, Optional

from db.types.user import User
from db.user_data_controller import UserDataController


class CacheUserController(UserDataController):

    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    def init_controller(self):
        pass

    def _create_user_impl(self, username: str, email: str, password: str) -> User:
        pass

    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    def get_all_users(self) -> List[User]:
        pass

    def delete_user(self, user_id: int):
        pass

    def shutdown_controller(self):
        pass