import datetime

from django.contrib.auth.hashers import make_password, check_password
from ninja import Router

from auth.schema import AuthBearer, Token, Login, Join
from common.schema import Message
from common.utils import make_nickname
from members.models import Member

router = Router()


@router.post('/login', response={200: Token, 400: Message})
def login(request, payload: Login):
    if not Member.objects.filter(email=payload.email):
        return 400, Message(message="Member is not exists")
    member = Member.objects.filter(email=payload.email).get()
    if not check_password(payload.password, member.password):
        return 400, Message(message="Password is not correct")
    token = AuthBearer().create_token(member.pk, payload.password)
    member.last_login_at = datetime.datetime.utcnow()
    member.save()
    return token


@router.post('/join', response={200: Message, 400: Message})
def join(request, payload: Join):
    if Member.objects.filter(email=payload.email):
        return 400, Message(message="Email already exists")
    nickname = make_nickname()
    while True:
        if Member.objects.filter(nickname=nickname):
            nickname = make_nickname()
        else:
            break
    payload.password = make_password(payload.password)
    payload.nickname = nickname
    Member.objects.create(**payload.dict())
    return Message(message="Success!")
