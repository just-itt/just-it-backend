from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File
from ninja.responses import codes_4xx

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error, Message
from common.utils.s3_upload import S3ImgUploader
from posts.models import Post, Image, TagOption
from posts.schema import PostOutWithImageAndTags, PostIn

router = Router(auth=AuthBearer())


@router.get("", response={200: List[PostOutWithImageAndTags], 401: Error})
def get_posts(request):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return (
        Post.objects.filter(author=request.auth.get("id"))
        .prefetch_related("tagoption_set")
        .all()
    )


@router.get("/{post_id}", response={200: PostOutWithImageAndTags, 401: Error})
def get_post(request, post_id: int):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return get_object_or_404(Post, id=post_id)


@router.post("", response={200: PostOutWithImageAndTags, codes_4xx: Error})
def add_post(request, payload: PostIn, image: UploadedFile = File(...)):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    post = Post.objects.create(
        title=payload.title, content=payload.content, author_id=request.auth.get("id")
    )
    image_url = S3ImgUploader().upload(file=image, domain=f"images/posts/{post.id}")
    Image.objects.create(post=post, image=image_url, ratio=payload.ratio)
    for tag_option in payload.tag_options:
        TagOption.objects.create(post=post, tag_option_id=tag_option)
    return post
