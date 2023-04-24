from typing import List

from ninja import Router

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error
from tags.models import Tag
from tags.schema import TagOutWithOptions

router = Router(auth=AuthBearer())


@router.get("", response={200: List[TagOutWithOptions], 401: Error})
def get_tags(request):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return Tag.objects.prefetch_related("option_set")
