from datetime import datetime
from enum import Enum
from typing import Optional

from ninja import Schema


class MemberStatusEnum(Enum):
    ACTIVE = "ACTIVE"
    WITHDRAW = "WITHDRAW"


class MemberIn(Schema):
    nickname: Optional[str]


class MemberOut(Schema):
    id: int
    email: str
    nickname: str
    profile_image: Optional[str]
    status: str
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class UpdatePassword(Schema):
    origin_password: str
    new_password: str
