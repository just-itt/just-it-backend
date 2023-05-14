from ninja import Schema


class Message(Schema):
    detail: str


class Error(Schema):
    detail: str


class IsSame(Schema):
    is_same: bool
