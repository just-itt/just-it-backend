from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field

from tags.schema import TagOptionOutWithTag


class PostImageOut(Schema):
    image: str
    ratio: str


class PostTagOut(Schema):
    tag_option: TagOptionOutWithTag = Field(None)


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
    tag_options: List[PostTagOut] = Field(None, alias="tagoption_set")
