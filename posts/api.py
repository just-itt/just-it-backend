from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File
from ninja.responses import codes_4xx

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error, Message
from common.utils.s3_upload import S3ImgUploader
from posts.models import Post, Image, TagOption
from posts.schema import PostOutWithImageAndTags, PostIn, CreatePost, UpdatePost

router = Router(auth=AuthBearer())


@router.get("", response={200: List[PostOutWithImageAndTags], 401: Error})
def get_posts(request):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return (
        Post.objects.filter(author=request.auth.get("id"), is_deleted=False)
        .prefetch_related("tagoption_set")
        .all()
    )


@router.get("/{post_id}", response={200: PostOutWithImageAndTags, 401: Error})
def get_post(request, post_id: int):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}
    return get_object_or_404(Post, id=post_id, is_deleted=False)


@router.post("", response={200: PostOutWithImageAndTags, codes_4xx: Error})
def create_post(request, payload: CreatePost, image: UploadedFile = File(...)):
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


@router.patch("/{post_id}", response={200: PostOutWithImageAndTags, 401: Error})
def update_post(
    request,
    post_id: int,
    payload: UpdatePost,
    image: Optional[UploadedFile] = File(...),
):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}

    post = get_object_or_404(Post, id=post_id, is_deleted=False)
    for attr, value in payload.dict().items():
        if value and (attr == "title" or attr == "content"):
            setattr(post, attr, value)
    post.save()

    if image:
        post_image = Image.objects.get(post=post)
        S3ImgUploader().delete(post_image.image)
        post_image.delete()
        image_url = S3ImgUploader().upload(file=image, domain=f"images/posts/{post.id}")
        Image.objects.create(post=post, image=image_url, ratio=payload.ratio)
    elif not image and payload.ratio:
        post_image = Image.objects.get(post=post)
        post_image.ratio = payload.ratio
        post_image.save()

    TagOption.objects.filter(post=post).delete()
    for tag_option in payload.tag_options:
        TagOption.objects.create(post=post, tag_option_id=tag_option)
    return post


@router.delete("/{post_id}", response={200: Message, 401: Error})
def delete_post(request, post_id: int):
    if request.auth == 401:
        return 401, {"message": "Unauthorized"}

    post = get_object_or_404(Post, id=post_id)
    post.is_deleted = True
    post.save()
    return 200, {"message": "Success!"}
