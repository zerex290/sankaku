from __future__ import annotations

from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from sankaku import types
from .users import Author
from .tags import PostTag
from .posts import Post


__all__ = ["PageBook", "Book"]


class BookState(BaseModel):
    current_page: int
    sequence: int
    post_id: int
    series_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    percent: int


class PageBook(BaseModel):
    id: int
    name_en: Optional[str]
    name_ja: Optional[str]
    description: str
    description_en: Optional[str]
    description_ja: Optional[str]
    created_at: datetime
    updated_at: datetime  # Not sure that update dt isn't optional
    author: Author
    is_public: bool
    is_active: bool
    is_flagged: bool
    post_count: int
    pages_count: int
    visible_post_count: int
    is_intact: bool
    rating: Optional[types.Rating]
    parent_id: Optional[int]
    has_children: Optional[bool]
    is_rating_locked: bool
    fav_count: int
    vote_count: int
    total_score: int
    comment_count: Optional[int]
    tags: list[PostTag]
    post_tags: list[PostTag]
    artist_tags: list[PostTag]
    genre_tags: list[PostTag]
    is_favorited: bool
    user_vote: Optional[int]
    posts: list[Post]
    file_url: Optional[str]
    sample_url: Optional[str]
    preview_url: Optional[str]
    cover_post: Optional[Post]
    reading: Optional[BookState]
    is_premium: bool
    is_pending: bool
    is_raw: bool
    is_trial: bool
    redirect_to_signup: bool
    locale: str
    is_deleted: bool
    cover_post_id: Optional[int]
    name: Optional[str]
    parent_pool: Optional[PageBook]


class Book(PageBook):
    child_pools: Optional[list[PageBook]]
    flagged_by_user: bool
    prem_post_count: int
