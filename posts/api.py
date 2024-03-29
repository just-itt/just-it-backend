from typing import List, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File, Query
from ninja.pagination import paginate

from accounts.schema import (
    AuthBearer,
)
from common.schema import Error, Message
from common.utils.auth import custom_auth
from common.utils.s3_upload import S3ImgUploader
from posts.models import Post, Image, Reply
from posts.schema import (
    PostOutWithImageAndTags,
    CreatePost,
    UpdatePost,
    ReplyIn,
    PostOutWithAll,
    ReplyOut,
    PostFilters,
)
from tags.models import Customization

router = Router(auth=AuthBearer())


@router.get("", auth=None, response={200: List[PostOutWithImageAndTags]})
@paginate
def get_posts(request, filters: PostFilters = Query(...)):
    search_query = Q()
    if filters.search_word:
        search_query.add(
            Q(title__icontains=filters.search_word)
            | Q(content__icontains=filters.search_word),
            search_query.AND,
        )
    if filters.tag_options:
        tag_options = [int(tag_option) for tag_option in filters.tag_options]
        search_query.add(Q(tag_options__in=tag_options), search_query.AND)
    search_query.add(Q(is_deleted=False), search_query.AND)
    return Post.objects.distinct().filter(search_query).order_by("-created_at").all()


@router.get("/custom", auth=custom_auth, response={200: List[PostOutWithImageAndTags]})
@paginate
def get_customization_posts(request):
    search_query = Q()
    if (
        request.auth != 401
        and Customization.objects.filter(member_id=request.auth.get("id")).exists()
        and Customization.objects.get(
            member_id=request.auth.get("id")
        ).tag_options.exists()
    ):
        custom_tag = Customization.objects.get(member_id=request.auth.get("id"))
        search_query.add(
            Q(tag_options__in=custom_tag.tag_options.filter()), search_query.AND
        )
    search_query.add(Q(is_deleted=False), search_query.AND)
    search_query.add(Q(image__ratio="1:1"), search_query.AND)
    return Post.objects.distinct().filter(search_query).order_by("-created_at").all()


@router.get("/me", response={200: List[PostOutWithImageAndTags], 401: Error})
@paginate
def get_my_posts(request, filters: PostFilters = Query(...)):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    search_query = Q()
    search_query.add(
        Q(author=request.auth.get("id")) & Q(is_deleted=False), search_query.AND
    )
    if filters.search_word:
        search_query.add(
            Q(title__icontains=filters.search_word)
            | Q(content__icontains=filters.search_word),
            search_query.AND,
        )
    if filters.tag_options:
        tag_options = [int(tag_option) for tag_option in filters.tag_options]
        search_query.add(Q(tag_options__in=tag_options), search_query.AND)
    return Post.objects.filter(search_query).order_by("-created_at").all()


@router.get("/bookmarks", response={200: List[PostOutWithImageAndTags], 401: Error})
@paginate
def get_bookmark_posts(request, filters: PostFilters = Query(...)):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    search_query = Q()
    search_query.add(
        Q(bookmarks__in=[request.auth.get("id")]) & Q(is_deleted=False),
        search_query.AND,
    )
    if filters.search_word:
        search_query.add(
            Q(title__icontains=filters.search_word)
            | Q(content__icontains=filters.search_word),
            search_query.AND,
        )
    if filters.tag_options:
        tag_options = [int(tag_option) for tag_option in filters.tag_options]
        search_query.add(Q(tag_options__in=tag_options), search_query.AND)
    return Post.objects.filter(search_query).order_by("-created_at").all()


@router.get("/{post_id}", auth=custom_auth, response={200: PostOutWithAll})
def get_post(request, post_id: int):
    post = Post.objects.filter(id=post_id, is_deleted=False).get()
    post.request = request
    return post


@router.post("", response={200: PostOutWithImageAndTags, 401: Error})
def create_post(request, payload: CreatePost, image: UploadedFile = File(...)):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    post = Post.objects.create(
        title=payload.title, content=payload.content, author_id=request.auth.get("id")
    )
    post.tag_options.set(payload.tag_options)
    image_url = S3ImgUploader().upload(file=image, domain=f"images/posts/{post.id}")
    Image.objects.create(post=post, image=image_url, ratio=payload.ratio)
    return post


@router.patch("/{post_id}", response={200: PostOutWithImageAndTags, 401: Error})
def update_post(
    request,
    post_id: int,
    payload: UpdatePost,
    image: Optional[UploadedFile] = File(None),
):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")

    post = get_object_or_404(
        Post, id=post_id, author_id=request.auth.get("id"), is_deleted=False
    )
    for attr, value in payload.dict().items():
        if value and (attr == "title" or attr == "content"):
            setattr(post, attr, value)
    post.tag_options.set(payload.tag_options)

    if image:
        if not payload.ratio:
            return 400, Error(detail="Ratio cannot be null")
        post_image = Image.objects.get(post=post)
        S3ImgUploader().delete(post_image.image)
        post_image.delete()
        image_url = S3ImgUploader().upload(file=image, domain=f"images/posts/{post.id}")
        Image.objects.create(post=post, image=image_url, ratio=payload.ratio)
    elif not image and payload.ratio:
        post_image = Image.objects.get(post=post)
        post_image.ratio = payload.ratio
        post_image.save()
    post.save()
    return post


@router.delete("/{post_id}", response={200: Message, 401: Error})
def delete_post(request, post_id: int):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")

    post = get_object_or_404(
        Post, id=post_id, author_id=request.auth.get("id"), is_deleted=False
    )
    post.is_deleted = True
    post.save()
    return Message(detail="Success!")


@router.post("/{post_id}/bookmarks", response={200: Message, 401: Error})
def create_post_bookmark(request, post_id: int):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    post = get_object_or_404(Post, id=post_id, is_deleted=False)
    post.bookmarks.add(request.auth.get("id"))
    return Message(detail="Success!")


@router.delete("/{post_id}/bookmarks", response={200: Message, 401: Error})
def delete_post_bookmark(request, post_id: int):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    post = get_object_or_404(Post, id=post_id, is_deleted=False)
    post.bookmarks.remove(request.auth.get("id"))
    return Message(detail="Success!")


@router.post("/{post_id}/replies", response={200: ReplyOut, 401: Error})
def create_post_reply(request, post_id: int, payload: ReplyIn):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    post = get_object_or_404(Post, id=post_id, is_deleted=False)
    reply = Reply.objects.create(
        post=post, author_id=request.auth.get("id"), content=payload.content
    )
    return reply


@router.patch("/{post_id}/replies/{reply_id}", response={200: ReplyOut, 401: Error})
def update_post_reply(request, post_id: int, reply_id: int, payload: ReplyIn):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    reply = get_object_or_404(
        Reply, author_id=request.auth.get("id"), id=reply_id, is_deleted=False
    )
    reply.content = payload.content
    reply.save()
    return reply


@router.delete("/{post_id}/replies/{reply_id}", response={200: Message, 401: Error})
def delete_post_reply(request, post_id: int, reply_id: int):
    if request.auth == 401:
        return 401, Error(detail="Unauthorized")
    reply = get_object_or_404(
        Reply, id=reply_id, author_id=request.auth.get("id"), is_deleted=False
    )
    reply.is_deleted = True
    reply.save()
    return Message(detail="Success!")
