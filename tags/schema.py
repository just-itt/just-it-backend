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

    @staticmethod
    def resolve_tag_title(obj):
        if not obj.tag:
            return None
        return obj.tag.title


class TagOut(Schema):
    id: int
    title: str
    is_required: bool
    created_at: datetime
    updated_at: Optional[datetime]


class TagOutWithOptions(TagOut):
    options: List[TagOptionOut] = Field(None, alias="option_set")


class CustomizationTagIn(Schema):
    title: str
    tag_options: List[int]


class CustomizationTagOut(Schema):
    id: int
    title: str
    tag_options: List[TagOptionOut] = None
    created_at: datetime
    updated_at: Optional[datetime]
