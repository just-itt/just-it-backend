from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field

from members.schema import MemberOut
from posts.models import Post
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
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]


class PostOutWithImageAndTags(PostOut):
    image: PostImageOut
    tag_options: List[TagOptionOutWithTag] = None


class PostOutWithAll(PostOutWithImageAndTags):
    replies: List[ReplyOut] = Field(..., alias="reply_set")
    is_bookmark: bool

    @staticmethod
    def resolve_replies(obj):
        replies = []
        for reply in obj:
            if reply.is_deleted:
                replies.append(reply)
        return replies

    @staticmethod
    def resolve_is_bookmark(obj):
        is_bookmark = Post.objects.filter(
            is_deleted=False, bookmarks__in=[obj.author_id]
        ).exists()
        return is_bookmark
