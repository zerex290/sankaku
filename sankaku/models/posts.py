from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import Field, validator

from sankaku import types
from sankaku.utils import convert_ts_to_datetime
from .base import SankakuResponseModel
from .tags import PostTag
from .users import Author


__all__ = ["Comment", "Post", "AIPost"]


class GenerationDirectives(SankakuResponseModel):
    """Model that describes additional fields for AI-generated posts."""
    width: int
    height: int
    prompt: str
    batch_size: int
    batch_count: int
    sampling_steps: int
    negative_prompt: str

    # The following fields can be missing in server JSON response
    version: Optional[str] = None  # https://imgur.com/a/aMJ7fR2


class BasePost(SankakuResponseModel):
    """Model that contains minimum amount of information that all posts have."""
    id: int
    created_at: datetime
    rating: types.Rating
    status: str
    author: Author
    file_url: Optional[str]
    preview_url: Optional[str]
    width: int
    height: int
    file_size: int
    extension: Optional[str] = Field(alias="file_type")
    generation_directives: Optional[GenerationDirectives]
    md5: str
    tags: List[PostTag]

    @property
    def file_type(self) -> Optional[types.FileType]:
        """Get type of the file."""
        if self.extension in ('png', 'jpeg', 'webp'):
            return types.FileType.IMAGE
        elif self.extension in ('webm', 'mp4'):
            return types.FileType.VIDEO
        elif self.extension in ('gif',):
            return types.FileType.GIF
        else:
            return None

    # Validators
    _normalize_datetime = (
        validator("created_at", pre=True, allow_reuse=True)
        (convert_ts_to_datetime)
    )

    @validator("extension", pre=True)
    def get_extension(cls, v) -> Optional[str]:  # noqa
        return v.split("/")[-1] if v else None


class Comment(SankakuResponseModel):
    """Model that describes comments related to posts if they are exist."""
    id: int
    created_at: datetime
    post_id: int
    author: Author
    body: str
    score: int
    parent_id: Optional[int]
    children: List[Comment]
    deleted: bool
    deleted_by: dict  # Seen only empty dictionaries so IDK real type
    updated_at: Optional[datetime]
    can_reply: bool
    reason: None  # Seen only None values so IDK real type


class Post(BasePost):
    """Model that describes posts."""
    sample_url: Optional[str]
    sample_width: int
    sample_height: int
    preview_width: Optional[int]
    preview_height: Optional[int]
    has_children: bool
    has_comments: bool
    has_notes: bool
    is_favorited: bool
    user_vote: Optional[int]
    parent_id: Optional[int]
    change: Optional[int]
    fav_count: int
    recommended_posts: int
    recommended_score: int
    vote_count: int
    total_score: int
    comment_count: Optional[int]
    source: Optional[str]
    in_visible_pool: bool
    is_premium: bool
    is_rating_locked: bool
    is_note_locked: bool
    is_status_locked: bool
    redirect_to_signup: bool
    sequence: Optional[int]
    video_duration: Optional[float]


class AIPost(BasePost):
    """Model that describes AI-generated posts.

    There is possibility that AI posts have the same fields as common posts,
    but premium account is needed to check it properly. So this model is
    actual for non-premium accounts.
    """
    updated_at: Optional[datetime]
    post_associated_id: Optional[int]

    # Validators
    _normalize_datetime = (
        validator("created_at", "updated_at", pre=True, allow_reuse=True)
        (convert_ts_to_datetime)
    )
