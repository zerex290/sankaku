from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from .posts import Comment, Post, AIPost
from .tags import PageTag
from .users import User, ShortenedUser


__all__ = ["CommentPage", "PostPage", "AIPage", "TagPage", "UserPage"]


class BasePage(BaseModel):
    number: int
    data: Sequence[Any]


class CommentPage(BasePage):
    data: Sequence[Comment]


class PostPage(BasePage):
    data: Sequence[Post]


class AIPage(BasePage):
    data: Sequence[AIPost]


class TagPage(BasePage):
    data: Sequence[PageTag]


class UserPage(BasePage):
    data: Sequence[User | ShortenedUser]
