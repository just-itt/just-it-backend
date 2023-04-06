import string
from random import choice

from common.consts import EMAIL_AUTH_CODE_SIZE


def make_auth_code() -> str:
    string_pool = string.digits
    return ''.join(choice(string_pool) for _ in range(EMAIL_AUTH_CODE_SIZE))
