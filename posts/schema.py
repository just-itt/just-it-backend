from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field

from members.schema import MemberOut
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
