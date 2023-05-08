from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from .posts import Post, AIPost
from .tags import Tag


__all__ = ["Page", "AIPage", "TagPage"]


class BasePage(BaseModel):
    number: int
    data: Sequence[Any]


class Page(BasePage):
    data: Sequence[Post]


class AIPage(BasePage):
    data: Sequence[AIPost]


class TagPage(BasePage):
    data: Sequence[Tag]
