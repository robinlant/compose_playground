from .dal_entities import UserEntity
from .exceptions import NotFoundException


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, UserEntity] = dict()
        self._last_id = -1

    def create_user(self, name: str, password: str) -> UserEntity:
        user = UserEntity(
            id=self._get_id(), name=name, password_hash=password
        )
        self._users[user.id] = user
        return user

    def get_users(self) -> list[UserEntity]:
        users = list()
        for user_id in self._users.keys():
            users.append(self._users[user_id])
        return users

    def get_user(self, user_id: int) -> UserEntity:
        if user_id in self._users:
            return self._users[user_id]
        raise NotFoundException(UserEntity, user_id)

    def update_user(self, user: UserEntity) -> None:
        if user.id in self._users:
            self._users[user.id] = user
            return
        raise NotFoundException(UserEntity, user.id)

    def delete_user(self, user_id: int) -> None:
        if user_id in self._users:
            self._users.pop(user_id)
            return
        raise NotFoundException(UserEntity, user_id)

    def _get_id(self) -> int:
        self._last_id += 1
        return self._last_id
