import datetime
from typing import Optional

import jwt
from ninja import Schema
from ninja.security import HttpBearer

from common.consts import TOKEN_VALID_SECONDS
from justit import settings


class AuthBearer(HttpBearer):
    # JWT secret key is set up in settings.py
    JWT_SIGNING_KEY = getattr(settings, "JWT_SIGNING_KEY", None)

    # TODO: 보강 필요
    def authenticate(self, request, token):
        try:
            if not self.JWT_SIGNING_KEY:
                return 401, {'message': 'Unauthorized'}
            jwt.decode(token, self.JWT_SIGNING_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return 401, {'message': 'Unauthorized'}
        except jwt.InvalidTokenError:
            return 401, {'message': 'Unauthorized'}
        else:
            return True

    def create_token(self, pk: int, email: str):
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_VALID_SECONDS)
        token = jwt.encode(
            {
                'id': pk,
                'email': email,
                'exp': expires.strftime("%Y-%m-%d %H:%M:%S")
            }, self.JWT_SIGNING_KEY)
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
