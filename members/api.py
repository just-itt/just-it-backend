from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.responses import codes_4xx

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error
from members.schema import MemberOut, MemberIn
from members.models import Member

router = Router(auth=AuthBearer())


@router.get("/me", response={200: MemberOut, 401: Error})
def get_member(request):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return get_object_or_404(Member, id=request.auth.get("id"))


@router.patch("/me", response={200: MemberOut, codes_4xx: Error})
def update_member(request, payload: MemberIn):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    member = get_object_or_404(Member, id=request.auth.get("id"))
    if member.nickname != payload.nickname and Member.objects.filter(
        nickname=payload.nickname
    ):
        return 400, {"message": "Nickname already exists"}
    for attr, value in payload.dict().items():
        if value:
            setattr(member, attr, value)
    member.save()
    return member
