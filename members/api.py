from django.shortcuts import get_object_or_404
from ninja import Router

from accounts.schema import (
    AuthBearer,
)
from common.schema import Message
from members.schema import MemberOut
from members.models import Member

router = Router(auth=AuthBearer())


@router.get("/me", response={200: MemberOut, 401: Message})
def me(request):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return get_object_or_404(Member, id=request.auth.get("id"))
