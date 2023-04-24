from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field


class TagOptionOut(Schema):
    id: int
    title: str


class TagOptionOutWithTag(Schema):
    id: int
    title: str
    tag_title: str


class TagOut(Schema):
    id: int
    title: str
    is_required: bool
    created_at: datetime
    updated_at: Optional[datetime]


class TagOutWithOptions(TagOut):
    options: List[TagOptionOut] = Field(None, alias="option_set")
