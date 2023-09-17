from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sankaku import types
from .base import SankakuResponseModel
from .posts import Post
from .tags import PostTag
from .users import Author


__all__ = ["PageBook", "Book"]


class BookState(SankakuResponseModel):
    current_page: int
    sequence: int
    post_id: int
    series_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    percent: int


class PageBook(SankakuResponseModel):
    """Model that describes books on book pages."""
    id: int  # noqa: A003
    name_en: Optional[str]
    name_ja: Optional[str]
    description: str
    description_en: Optional[str]
    description_ja: Optional[str]
    created_at: datetime
    updated_at: datetime
    author: Optional[Author]
    is_public: bool
    is_active: bool
    is_flagged: bool
    post_count: int
    pages_count: int
    visible_post_count: int
    is_intact: bool
    rating: Optional[types.Rating]
    reactions: List  # TODO: Search for books with non-empty reactions
    parent_id: Optional[int]
    has_children: Optional[bool]
    is_rating_locked: bool
    fav_count: int
    vote_count: int
    total_score: int
    comment_count: Optional[int]
    tags: List[PostTag]
    post_tags: List[PostTag]
    artist_tags: List[PostTag]
    genre_tags: List[PostTag]
    is_favorited: bool
    user_vote: Optional[int]
    posts: List[Optional[Post]]
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
    """Model that describes specific book."""
    child_pools: Optional[List[PageBook]]
    flagged_by_user: bool
    prem_post_count: int
