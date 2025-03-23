import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from fastapi import status
from pydantic import BaseModel

from src.bll.bll_exceptions import WrongCredentialsException
from src.bll.user_service import UserService
from .error_or import ErrorOr


class Token(BaseModel):
    user_id: int
    user_name: str
    valid_before: datetime


class JWTService:
    def __init__(self, app_secret: bytes, user_service: UserService, hours_valid: int = 6):
        self.app_secret = app_secret
        self.user_service = user_service
        self.delta_valid = timedelta(hours=hours_valid)

    def issue_token(self, username: str, password: str) -> ErrorOr[str]:
        try:
            user = self.user_service.login(user_id=username, user_password=password)
            valid_before = datetime.now(tz=timezone.utc) + self.delta_valid
            token = Token(user_id=user.id, user_name=user.name, valid_before=valid_before).model_dump_json()

            return ErrorOr(self._create_jwt(token))
        except WrongCredentialsException:
            return ErrorOr(is_error=True, error_code=status.HTTP_401_UNAUTHORIZED)

    def verify_token(self, token: str) -> ErrorOr[tuple[int, str]]:
        try:
            payload, signature = self._decode_token(token)
        except binascii.Error:
            return ErrorOr(is_error=True, error_code=status.HTTP_401_UNAUTHORIZED, error_msg="Token is invalid")
        base64_token = base64.standard_b64encode(payload.encode()).decode().rstrip("=")
        recreated_signature = hmac.new(self.app_secret, base64_token.encode(), hashlib.sha256).digest()

        if recreated_signature != signature:
            return ErrorOr(is_error=True, error_code=status.HTTP_401_UNAUTHORIZED, error_msg="Token is invalid")
        token = Token(**json.loads(payload))
        if token.valid_before <= datetime.now(tz=timezone.utc):
            return ErrorOr(is_error=True, error_code=status.HTTP_401_UNAUTHORIZED, error_msg="Token expired")
        return ErrorOr((token.user_id, token.user_name))

    @staticmethod
    def _decode_token(token: str) -> tuple[str, bytes]:
        payload_b64, signature_b64 = token.split(".")

        payload = base64.standard_b64decode(payload_b64 + "==").decode()

        signature = base64.standard_b64decode(signature_b64 + "==")

        return payload, signature

    def _create_jwt(self, payload: str) -> str:
        base64_token = base64.standard_b64encode(payload.encode()).decode().rstrip("=")

        signature = hmac.new(self.app_secret, base64_token.encode(), hashlib.sha256).digest()

        encoded_signature = base64.standard_b64encode(signature).decode().rstrip("=")

        return f"{base64_token}.{encoded_signature}"
