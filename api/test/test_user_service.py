from unittest.mock import MagicMock

import pytest

from src.bll.bll_exceptions import UserExistsException, FalseStringFormatException, UnallowedCharactersException, \
    WrongCredentialsException, ModelNotFound
from src.bll.user_service import UserService
from src.dal import UserEntity
from src.dal.exceptions import DalUniqueViolationException
from src.dal.repositories import UserRepository


def _generate_pw_hash(password: str) -> str:
    return "hash" + password


@pytest.fixture()
def user_entity() -> UserEntity:
    password_hash = _generate_pw_hash("password")
    return UserEntity(id=1, name="bob", password_hash=password_hash)


@pytest.fixture()
def user_entities() -> list[UserEntity]:
    pw_hash = _generate_pw_hash("password")
    return [
        UserEntity(id=1, name="bobi", password_hash=pw_hash),
        UserEntity(id=2, name="bob8", password_hash=pw_hash),
        UserEntity(id=3, name="bob", password_hash=pw_hash)
    ]


def test_create_user_user_info_user_created(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.create_user.return_value = user_entity
    user_repository.get_user_by_name.return_value = user_entity
    user_service = UserService(user_repository=user_repository)

    # Act
    user = user_service.create_user(name=user_entity.name, password="password")

    # Assert
    assert user.id == user_entity.id
    assert user.name == user_entity.name
    user_repository.get_user_by_name.assert_called_once_with(name=user_entity.name)
    user_repository.create_user.assert_called_once_with(name=user_entity.name, password_hash=user_entity.password_hash)


def test_create_user_user_exists_raises_exception():
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.create_user.side_effect = DalUniqueViolationException(table_name="some_table",
                                                                          columnn_name="some_column",
                                                                          identifier="some_identifier")
    user_service = UserService(user_repository=user_repository)

    # Act & Assert
    with pytest.raises(UserExistsException):
        user_service.create_user(name="bob", password="password")


def test_create_user_short_name_raises_exception():
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_service = UserService(user_repository=user_repository)

    # Act & Assert
    with pytest.raises(FalseStringFormatException):
        user_service.create_user(name="bo", password="password")


def test_create_user_wrong_name_raises_exception():
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_service = UserService(user_repository=user_repository)

    # Act & Assert
    with pytest.raises(UnallowedCharactersException):
        user_service.create_user(name="b%%o", password="password")


def test_get_user_user_exists_returns_model(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity
    user_repository.get_user_by_name.return_value = user_entity

    # Act
    user_service = UserService(user_repository=user_repository)
    u1 = user_service.get_user(user_entity.id)
    u2 = user_service.get_user(user_entity.name)

    # Assert
    assert u1 == u2
    assert u1.id == user_entity.id
    assert u1.name == user_entity.name
    user_repository.get_user_by_id.assert_called_with(user_id=user_entity.id)
    user_repository.get_user_by_name.assert_called_with(name=user_entity.name)


def test_get_user_user_not_exists_returns_none():
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = None
    user_repository.get_user_by_name.return_value = None

    # Act
    user_service = UserService(user_repository=user_repository)
    u1 = user_service.get_user(1)
    u2 = user_service.get_user("blabla")

    # Assert
    assert u1 == u2
    assert u1 is None


def test_get_users_all_users_returns_models(user_entities: list[UserEntity]):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_users.return_value = user_entities

    # Act
    user_service = UserService(user_repository=user_repository)
    users = user_service.get_users()

    # Assert
    for model, entity in zip(users, user_entities):
        assert model.id == entity.id
        assert model.name == entity.name
    user_repository.get_users.assert_called_with(user_ids=None)


def test_delete_users_right_credentials_returns_none(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity

    # Act
    user_service = UserService(user_repository=user_repository)
    user_service.delete_user(user_id=user_entity.id, password="password")

    # Assert
    user_repository.get_user_by_id.assert_called_with(user_id=user_entity.id)
    user_repository.delete_user.assert_called_with(user_id=user_entity.id)


def test_delete_users_wrong_credentials_raises_exception(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity

    # Act
    with pytest.raises(WrongCredentialsException):
        user_service = UserService(user_repository=user_repository)
        user_service.delete_user(user_id=user_entity.id, password="wrong_password")

    # Assert
    user_repository.get_user_by_id.assert_called_with(user_id=user_entity.id)
    user_repository.delete_user.assert_not_called()


def test_delete_users_wrong_user_id_raises_exception():
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = None

    # Act
    user_service = UserService(user_repository=user_repository)
    with pytest.raises(ModelNotFound):
        user_service.delete_user(user_id=1, password="some_password")

    # Assert
    user_repository.get_user_by_id.assert_called_with(user_id=1)


def test_change_password_right_credentials_returns_none(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity
    user_repository.update_user.return_value = None

    # Act
    user_service = UserService(user_repository=user_repository)
    user_service.change_password(user_entity.id, "password", "new_password")

    # Assert
    user_repository.update_user.assert_called_with(
        user=UserEntity(id=user_entity.id, name=user_entity.name, password_hash=_generate_pw_hash("new_password")))


def test_change_password_wrong_credentials_raises_exception(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity
    user_repository.update_user.return_value = None

    # Act
    with pytest.raises(WrongCredentialsException):
        user_service = UserService(user_repository=user_repository)
        user_service.change_password(user_entity.id, "wrong_password", "new_password")

    # Assert
    user_repository.update_user.assert_not_called()


def test_change_username_right_credentials_returns_none(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity
    user_repository.update_user.return_value = None

    # Act
    user_service = UserService(user_repository=user_repository)
    user_service.change_username(user_id=user_entity.id, user_password="password", new_username="new_username")

    # Assert
    user_repository.update_user.assert_called_with(
        user=UserEntity(id=user_entity.id, name="new_username", password_hash=user_entity.password_hash))


def test_login_right_credentials_returns_user_model(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity

    # Act
    user_service = UserService(user_repository=user_repository)
    res = user_service.login(user_id=user_entity.id, user_password="password")

    # Assert
    assert user_entity.id == res.id
    assert res.name == user_entity.name


def test_login_wrong_credentials_raises_exception(user_entity: UserEntity):
    # Arrange
    user_repository = MagicMock(spec=UserRepository)
    user_repository.get_user_by_id.return_value = user_entity

    # Act & Assert
    with pytest.raises(WrongCredentialsException):
        user_service = UserService(user_repository=user_repository)
        res = user_service.login(user_id=user_entity.id, user_password="wrong_password")
