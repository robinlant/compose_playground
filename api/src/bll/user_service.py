import re

from src.dal import UserRepository, UserEntity
from src.dal.exceptions import DalUniqueViolationException
from .bll_exceptions import (
    UserExistsException,
    DatabaseExcetpion,
    UnallowedCharactersException,
    FalseStringFormatException,
    ModelNotFound, WrongCredentialsException
)
from .bll_models import UserModel


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def create_user(self, name: str, password: str) -> UserModel:
        try:
            password_hash = _generate_pw_hash(password)
            name = name.lower().strip()
            self._validate_username(name=name)
            self._user_repository.create_user(name=name.lower(), password_hash=password_hash)
            user = self._user_repository.get_user_by_name(name=name)
            if user is None:
                raise DatabaseExcetpion("Error while creating user")
            return self._to_model(user)
        except DalUniqueViolationException:
            raise UserExistsException(name)

    def get_user(self, identifier: str | int) -> UserModel | None:
        if isinstance(identifier, int):
            user = self._user_repository.get_user_by_id(user_id=identifier)
        else:
            user = self._user_repository.get_user_by_name(name=identifier)
        if user is None:
            return None
        return self._to_model(user)

    def get_users(self, user_ids: list[int] | None = None) -> list[UserModel]:
        users = self._user_repository.get_users(user_ids=user_ids)
        return [self._to_model(user) for user in users]

    def delete_user(self, user_id: int, password: str) -> None:
        self._validate_password(password=password, user_id=user_id)
        self._user_repository.delete_user(user_id=user_id)
        return None

    def change_password(self, user_id: int, user_password: str, new_password: str) -> None:
        user = self._user_repository.get_user_by_id(user_id)
        self._ensure_found(user, user_id)
        self._validate_password(password=user_password, user_id=user_id)
        user.password_hash = _generate_pw_hash(password=new_password)
        self._user_repository.update_user(user=user)

    def change_username(self, user_id: int, user_password: str, new_username: str) -> UserModel:
        user = self._user_repository.get_user_by_id(user_id)
        self._ensure_found(user, user_id)
        self._validate_password(password=user_password, user_id=user_id)
        user.name = new_username
        self._user_repository.update_user(user=user)

    def _validate_password(self, password: str, user_id: int | str):
        if isinstance(user_id, int):
            user = self._user_repository.get_user_by_id(user_id=user_id)
        else:
            user = self._user_repository.get_user_by_name(name=user_id)
        self._ensure_found(user, user_id)
        hashed_password = _generate_pw_hash(password)
        if hashed_password != user.password_hash:
            raise WrongCredentialsException(msg="Wrong password")

    def login(self, user_id: int | str, user_password: str) -> UserModel:
        self._validate_password(password=user_password, user_id=user_id)
        return self.get_user(user_id)

    @staticmethod
    def _ensure_found(user_entity: UserEntity | None, identifier: int | None = None) -> UserEntity:
        if user_entity is None:
            raise ModelNotFound(f"User {identifier} not found")
        return user_entity

    @staticmethod
    def _validate_username(name: str):
        if len(name) < 3:
            raise FalseStringFormatException(msg="Username must be at least 3 characters long", string=name)
        if not re.fullmatch(r"^[a-z_0-9-]+$", name):
            raise UnallowedCharactersException("Only a-z, 0-9 and _ are allowed in usernames", name)

    @staticmethod
    def _to_model(user: UserEntity) -> UserModel:
        return UserModel(id=user.id, name=user.name)


def _generate_pw_hash(password: str) -> str:
    return "hash" + password
