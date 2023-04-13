import datetime
import time
from enum import Enum
from typing import Optional

import jwt
from ninja import Schema
from ninja.security import HttpBearer

from common.consts import TOKEN_VALID_MINUTES
from justit import settings


class AuthBearer(HttpBearer):
    JWT_SIGNING_KEY = getattr(settings, "JWT_SIGNING_KEY", None)

    def authenticate(self, request, token):
        try:
            if not self.JWT_SIGNING_KEY:
                return 401
            decoded_token = jwt.decode(
                token, self.JWT_SIGNING_KEY, algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return 401
        except jwt.InvalidTokenError:
            return 401
        else:
            return decoded_token

    def create_token(self, pk: int, email: str):
        expires = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=TOKEN_VALID_MINUTES
        )
        expires_timestamp = int(time.mktime(expires.timetuple()))
        token = jwt.encode(
            {"id": pk, "email": email, "exp": expires_timestamp},
            self.JWT_SIGNING_KEY,
        )
        return Token(token=token, expires=expires)


class Token(Schema):
    token: str
    expires: datetime.datetime


class Login(Schema):
    email: str
    password: str


class Join(Schema):
    email: str
    password: str
    nickname: Optional[str]


class EmailAuthentication(Schema):
    email: str


class EmailAuthenticationCode(EmailAuthentication):
    auth_code: str


class EmailAuthenticationTypeEnum(Enum):
    JOIN = "JOIN"
    PASSWORD = "PASSWORD"
