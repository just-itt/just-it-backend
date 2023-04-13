import datetime

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from ninja import Router

from accounts.models import EmailAuth
from accounts.schema import (
    AuthBearer,
    Token,
    Login,
    Join,
    EmailAuthentication,
    EmailAuthenticationCode,
)
from accounts.utils import make_auth_code
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
    token = AuthBearer().create_token(member.pk, payload.email)
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


@router.post("/email-auth/send", response={200: Message, 400: Message})
def email_auth_send(request, payload: EmailAuthentication):
    if Member.objects.filter(email=payload.email):
        return 400, Message(message="Email already authorized")
    auth_code = make_auth_code()
    EmailAuth.objects.create(
        email=payload.email,
        auth_code=auth_code,
        expire_at=datetime.datetime.utcnow()
        + datetime.timedelta(minutes=EMAIL_AUTH_CODE_VALID_MINUTES),
    )
    EmailMessage(
        subject="[Just it] 인증 코드", body=f"인증 코드는 [{auth_code}]입니다.", to=[payload.email]
    ).send()
    return Message(message="Success!")


@router.post("/email-auth/check", response={200: Message, 400: Message})
def email_auth_check(request, payload: EmailAuthenticationCode):
    email_auth = EmailAuth.objects.filter(email=payload.email).last()
    utc_now = datetime.datetime.utcnow()
    if email_auth.auth_code != payload.auth_code:
        return 400, Message(message="Authentication code is not valid")
    if email_auth.expire_at < utc_now:
        return 400, Message(message="Authentication code has expired")
    EmailAuth.objects.filter(email=payload.email).all().delete()
    return Message(message="Success!")
