import datetime

from django.contrib.auth.hashers import make_password, check_password
from ninja import Router

from auth.models import Email
from auth.schema import AuthBearer, Token, Login, Join, EmailAuthentication
from auth.utils import make_auth_code
from common.consts import EMAIL_AUTH_CODE_VALID_MINUTES
from common.schema import Message
from members.utils import make_nickname
from members.models import Member

router = Router()


@router.post("/login", response={200: Token, 400: Message})
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


@router.post("/join", response={200: Message, 400: Message})
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


@router.post("/email", response={200: Message, 400: Message})
def email_auth(request, payload: EmailAuthentication):
    if Member.objects.filter(email=payload.email):
        return 400, Message(message="Email already authorized")
    auth_code = make_auth_code()
    Email.objects.create(
        email=payload.email,
        auth_code=auth_code,
        expire_at=datetime.datetime.utcnow()
        + datetime.timedelta(minutes=EMAIL_AUTH_CODE_VALID_MINUTES),
    )
    return Message(message="Success!")


@router.post("/email/check", response={200: Message, 400: Message})
def email_auth(request, payload: EmailAuthentication):
    email_auth = Email.objects.filter(email=payload.email, is_certified=False).first()
    utc_now = datetime.datetime.utcnow()
    if email_auth.auth_code != payload.auth_code:
        return 400, Message(message="Authentication code is not valid")
    if email_auth.expire_at < utc_now:
        return 400, Message(message="Authentication code has expired")
    email_auth.is_certified = True
    email_auth.certified_at = utc_now
    return Message(message="Success!")
