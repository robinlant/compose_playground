from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from src.bll.bll_models import UserModel
from src.bll.user_service import UserService
from src.view.jwt_service import JWTService


@pytest.fixture()
def user_model() -> UserModel:
    return UserModel(id=1, name="bob")


@pytest.fixture()
def app_secret() -> bytes:
    return bytes("secret_key", "utf-8")


def test_jwt_service_issue_token_return_token(user_model: UserModel, app_secret: bytes):
    # Arrange
    user_service = MagicMock(spec=UserService)
    user_service.login.return_value = user_model

    # Act
    jwt_service = JWTService(user_service=user_service, app_secret=app_secret)
    token = jwt_service.issue_token(user_model.name, "password").return_or_raise_http_exception()
    print(token)

    # Assert
    user_service.login.assert_called_once_with(user_id=user_model.name, user_password="password")


def test_decode_token_valid_token_returns_userid_name(user_model: UserModel, app_secret: bytes):
    # Arrange
    user_service = MagicMock(spec=UserService)
    user_service.login.return_value = user_model

    # Act
    jwt_service = JWTService(user_service=user_service, app_secret=app_secret)
    token = jwt_service.issue_token(user_model.name, "password").return_or_raise_http_exception()
    user_id, user_name = jwt_service.verify_token(token).return_or_raise_http_exception()

    # Assert
    assert user_id == user_model.id
    assert user_name == user_model.name
    user_service.login.assert_called_once_with(user_id=user_model.name, user_password="password")


def test_decode_token_invalid_token_raises_exception(user_model: UserModel, app_secret: bytes):
    # Arrange
    user_service = MagicMock(spec=UserService)
    user_service.login.return_value = user_model

    # Act
    jwt_service = JWTService(user_service=user_service, app_secret=app_secret)
    token = jwt_service.issue_token(user_model.name, "password").return_or_raise_http_exception()
    with pytest.raises(HTTPException):
        jwt_service.verify_token("invalid" + token + "invalid").return_or_raise_http_exception()

    # Assert
    user_service.login.assert_called_once_with(user_id=user_model.name, user_password="password")


def test_decode_token_expired_token_raises_exception(user_model: UserModel, app_secret: bytes):
    # Arrange
    user_service = MagicMock(spec=UserService)
    user_service.login.return_value = user_model

    # Act
    jwt_service = JWTService(user_service=user_service, app_secret=app_secret, hours_valid=-1)
    token = jwt_service.issue_token(user_model.name, "password").return_or_raise_http_exception()
    with pytest.raises(HTTPException):
        jwt_service.verify_token(token).return_or_raise_http_exception()

    # Assert
    user_service.login.assert_called_once_with(user_id=user_model.name, user_password="password")
