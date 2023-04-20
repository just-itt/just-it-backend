import datetime

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from ninja import Router

from accounts.models import EmailAuth
from accounts.schema import (
    AuthBearer,
    Token,
    Login,
    Join,
    EmailAuthentication,
    EmailAuthenticationCode,
    EmailAuthenticationTypeEnum,
)
from accounts.utils import make_auth_code
from common.consts import EMAIL_AUTH_CODE_VALID_MINUTES
from common.schema import Message, Error
from members.schema import MemberStatusEnum
from members.utils import make_nickname
from members.models import Member

router = Router()


@router.post("/login", response={200: Token, 400: Error})
def login(request, payload: Login):
    member = get_object_or_404(
        Member, email=payload.email, status=MemberStatusEnum.ACTIVE.value
    )
    if not check_password(payload.password, member.password):
        return 400, Message(message="Password is not correct")
    token = AuthBearer().create_token(member.pk, payload.email)
    member.last_login_at = datetime.datetime.utcnow()
    member.save()
    return token


@router.post("/join", response={200: Message, 400: Error})
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


@router.post("/email-auth/send", response={200: Message, 400: Error})
def join_auth_send(request, payload: EmailAuthentication):
    if Member.objects.filter(email=payload.email):
        return 400, Message(message="Email already authorized")
    auth_code = make_auth_code()
    EmailAuth.objects.create(
        email=payload.email,
        auth_code=auth_code,
        expire_at=datetime.datetime.utcnow()
        + datetime.timedelta(minutes=EMAIL_AUTH_CODE_VALID_MINUTES),
        type=EmailAuthenticationTypeEnum.JOIN.value,
    )
    EmailMessage(
        subject="[Just it] 회원 가입 인증 코드",
        body=f"회원 가입 인증 코드는 [{auth_code}]입니다.",
        to=[payload.email],
    ).send()
    return Message(message="Success!")


@router.post("/email-auth/check", response={200: Message, 400: Error})
def join_auth_check(request, payload: EmailAuthenticationCode):
    email_auth = EmailAuth.objects.filter(
        email=payload.email, type=EmailAuthenticationTypeEnum.JOIN.value
    ).last()
    utc_now = datetime.datetime.utcnow()
    if email_auth.auth_code != payload.auth_code:
        return 400, Message(message="Authentication code is not valid")
    if email_auth.expire_at < utc_now:
        return 400, Message(message="Authentication code has expired")
    EmailAuth.objects.filter(
        email=payload.email, type=EmailAuthenticationTypeEnum.JOIN.value
    ).all().delete()
    return Message(message="Success!")


@router.post("/find-pw/send", response={200: Message, 400: Error})
def find_password_auth_send(request, payload: EmailAuthentication):
    get_object_or_404(Member, email=payload.email, status=MemberStatusEnum.ACTIVE.value)
    auth_code = make_auth_code()
    EmailAuth.objects.create(
        email=payload.email,
        auth_code=auth_code,
        expire_at=datetime.datetime.utcnow()
        + datetime.timedelta(minutes=EMAIL_AUTH_CODE_VALID_MINUTES),
        type=EmailAuthenticationTypeEnum.PASSWORD.value,
    )
    EmailMessage(
        subject="[Just it] 비밀 번호 찾기 인증 코드",
        body=f"비밀 번호 찾기 인증 코드는 [{auth_code}]입니다.",
        to=[payload.email],
    ).send()
    return Message(message="Success!")


@router.post("/find-pw/check", response={200: Message, 400: Error})
def find_password_auth_check(request, payload: EmailAuthenticationCode):
    email_auth = EmailAuth.objects.filter(
        email=payload.email,
        type=EmailAuthenticationTypeEnum.PASSWORD.value,
        expire_at__gte=datetime.datetime.utcnow(),
        is_auth=False,
    ).last()
    if not email_auth:
        return 400, {"message": "Email authentication has not been completed"}
    if email_auth.auth_code != payload.auth_code:
        return 400, Message(message="Authentication code is not valid")
    email_auth.is_auth = True
    email_auth.save()
    return Message(message="Success!")


@router.patch("/reset-pw", response={200: Message, 400: Error})
def reset_password(request, payload: Login):
    email_auth = EmailAuth.objects.filter(
        email=payload.email,
        type=EmailAuthenticationTypeEnum.PASSWORD.value,
        is_auth=True,
        expire_at__gte=datetime.datetime.utcnow(),
    )
    if not email_auth:
        return 400, {"message": "Email authentication has not been completed"}
    member = get_object_or_404(
        Member, email=payload.email, status=MemberStatusEnum.ACTIVE.value
    )
    member.password = make_password(payload.password)
    member.save()
    EmailAuth.objects.filter(
        email=payload.email, type=EmailAuthenticationTypeEnum.PASSWORD.value
    ).all().delete()
    return Message(message="Success!")
