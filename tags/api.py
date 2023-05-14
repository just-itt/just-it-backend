from typing import List

from ninja import Router

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error
from tags.models import Tag, Customization
from tags.schema import TagOutWithOptions, CustomizationTagIn, CustomizationTagOut

router = Router(auth=AuthBearer())


@router.get("", response={200: List[TagOutWithOptions], 401: Error})
def get_tags(request):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    return Tag.objects.prefetch_related("option_set")


@router.get("/me", response={200: CustomizationTagOut, 401: Error})
def get_customization_tags(request):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    custom_tag = Customization.objects.get(member_id=request.auth.get("id"))
    return custom_tag


@router.post("/me", response={200: CustomizationTagOut, 401: Error})
def create_customization_tags(request, payload: CustomizationTagIn):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    if Customization.objects.filter(member_id=request.auth.get("id")).exists():
        custom_tag = Customization.objects.get(member_id=request.auth.get("id"))
        custom_tag.title = payload.title
        custom_tag.tag_options.set(payload.tag_options)
    else:
        custom_tag = Customization.objects.create(
            title=payload.title, member_id=request.auth.get("id")
        )
        custom_tag.tag_options.set(payload.tag_options)
    return custom_tag
