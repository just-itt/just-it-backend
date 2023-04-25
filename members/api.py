from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File
from ninja.responses import codes_4xx

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error, Message
from common.utils.s3_upload import S3ImgUploader
from members.schema import MemberOut, MemberIn, MemberStatusEnum, UpdatePassword
from members.models import Member

router = Router(auth=AuthBearer())


@router.get("/me", response={200: MemberOut, 401: Error})
def get_member(request):
    if request.auth == 401:
        return 401, Error(message="Unauthorized")
    return get_object_or_404(Member, id=request.auth.get("id"))


@router.patch("/me", response={200: MemberOut, codes_4xx: Error})
def update_member(request, payload: MemberIn):
    if request.auth == 401:
        return 401, Error(message="Unauthorized")
    member = get_object_or_404(Member, id=request.auth.get("id"))
    if member.nickname != payload.nickname and Member.objects.filter(
        nickname=payload.nickname
    ):
        return 400, Error(message="Nickname already exists")
    for attr, value in payload.dict().items():
        if value:
            setattr(member, attr, value)
    member.save()
    return member


@router.patch("/withdraw", response={200: Message})
def withdraw(request):
    if request.auth == 401:
        return 401, Error(message="Unauthorized")
    member = get_object_or_404(
        Member, id=request.auth.get("id"), status=MemberStatusEnum.ACTIVE.value
    )
    member.status = MemberStatusEnum.WITHDRAW.value
    member.save()
    return Message(message="Success!")


@router.post("/me/profile-image", response={200: MemberOut, codes_4xx: Error})
def create_member_profile_image(request, file: UploadedFile = File(...)):
    if request.auth == 401:
        return 401, Error(message="Unauthorized")
    member = get_object_or_404(
        Member, id=request.auth.get("id"), status=MemberStatusEnum.ACTIVE.value
    )
    if member.profile_image:
        S3ImgUploader().delete(member.profile_image)
    member.profile_image = S3ImgUploader().upload(
        file=file, domain=f"images/members/{member.id}"
    )
    member.save()
    return member


@router.delete("/me/profile-image", response={200: MemberOut, codes_4xx: Error})
def delete_member_profile_image(request):
    if request.auth == 401:
        return 401, Error(message="Unauthorized")
    member = get_object_or_404(
        Member, id=request.auth.get("id"), status=MemberStatusEnum.ACTIVE.value
    )
    if member.profile_image:
        if S3ImgUploader().delete(member.profile_image):
            member.profile_image = None
            member.save()
    return member


@router.patch("/me/pw", response={200: Message, 400: Error})
def update_password(request, payload: UpdatePassword):
    member = get_object_or_404(
        Member, id=request.auth.get("id"), status=MemberStatusEnum.ACTIVE.value
    )
    if member.password != make_password(payload.origin_password):
        return 400, Error(message="Password is not correct")
    member.password = make_password(payload.new_password)
    member.save()
    return Message(message="Success!")
