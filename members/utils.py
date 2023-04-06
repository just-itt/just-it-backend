import string
from random import choice

from common.consts import NICKNAME_CODE_SIZE, NICKNAME_PREFIX


def make_nickname() -> str:
    string_pool = string.digits
    random_num = ''.join(choice(string_pool) for _ in range(NICKNAME_CODE_SIZE))
    return f"{NICKNAME_PREFIX}{random_num}"
