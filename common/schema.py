from ninja import Schema


class Message(Schema):
    message: str


class Error(Schema):
    message: str
