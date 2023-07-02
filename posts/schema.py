from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field

from members.schema import MemberOut
from posts.models import Post, Reply
from tags.schema import TagOptionOutWithTag


class PostImageOut(Schema):
    image: str
    ratio: str


class ReplyIn(Schema):
    content: str


class ReplyOut(Schema):
    id: int
    post_id: int
    content: str
    author: MemberOut
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]


class PostIn(Schema):
    title: str
    content: str


class CreatePost(PostIn):
    ratio: str
    tag_options: List[int]


class UpdatePost(PostIn):
    ratio: Optional[str]
    tag_options: List[int]


class PostOut(Schema):
    id: int
    title: str
    content: str
    author: MemberOut
    created_at: datetime
    updated_at: Optional[datetime]


class PostOutWithImageAndTags(PostOut):
    image: PostImageOut
    tag_options: List[TagOptionOutWithTag] = None


class PostOutWithAll(PostOutWithImageAndTags):
    replies: List[ReplyOut]
    is_bookmark: bool

    @staticmethod
    def resolve_replies(obj):
        return (
            Reply.objects.filter(post_id=obj.id, is_deleted=False)
            .order_by("created_at")
            .all()
        )

    @staticmethod
    def resolve_is_bookmark(obj):
        if obj.request.auth and type(obj.request.auth) == dict:
            return Post.objects.filter(
                id=obj.id, is_deleted=False, bookmarks__in=[obj.request.auth.get("id")]
            ).exists()
        else:
            return False


class PostFilters(Schema):
    search_word: Optional[str] = Field(None)
    tag_options: Optional[List[int]] = Field(None)
