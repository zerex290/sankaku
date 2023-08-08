from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import Field, field_validator

from sankaku import types
from sankaku.utils import convert_ts_to_datetime
from .base import SankakuResponseModel
from .tags import PostTag
from .users import Author


__all__ = ["Comment", "Post", "AIPost"]


class GenerationDirectives(SankakuResponseModel):
    # Model fields were tested on 100 pages.
    # TODO: Check fields of nested objects.

    tags: List[dict]
    # Possible JSON object properties:
    #   - id: int
    #   - name: str
    #   - type: int
    #   - count: int
    #   - rating: str
    #   - name_en: str
    #   - name_ja: str
    #   - tagName: str
    #   - pool_count: int
    #   - post_count: int
    #   - series_count: int
    #   tag_translations: list[Any]  # IDK list items types

    aspect_ratio: Optional[dict] = None
    # Possible JSON object properties:
    #   - type: str
    #   - width: int
    #   - height: int

    rating: Optional[dict] = None
    # Possible JSON object properties:
    #   - value: str
    #   - default: str

    negative_prompt: Optional[str] = None
    natural_input: Optional[str] = None
    denoising_strength: Optional[int] = None


class AIGenerationDirectives(SankakuResponseModel):
    """Model that describes additional fields for AI-generated posts."""
    # TODO: Check response model fields more carefully.
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
    id: int  # noqa: A003
    created_at: datetime
    rating: types.Rating
    status: str
    author: Author
    file_url: Optional[str]
    preview_url: Optional[str]
    width: int
    height: int
    file_size: int
    file_type: Optional[types.FileType]
    extension: Optional[str] = Field(alias="file_type")
    md5: str
    tags: List[PostTag]

    @field_validator("file_type", mode="before")
    @classmethod
    def get_file_type_and_extension(cls, v) -> Optional[types.FileType]:
        return types.FileType(v.split("/")[0]) if v else None

    @field_validator("created_at", mode="before")
    @classmethod
    def normalize_datetime(cls, v) -> Optional[datetime]:
        return convert_ts_to_datetime(v)

    @field_validator("extension", mode="before")
    @classmethod
    def get_extension(cls, v) -> Optional[str]:
        return v.split("/")[-1] if v else None


class Comment(SankakuResponseModel):
    """Model that describes comments related to posts if they are exist."""
    # TODO: Check response model fields more carefully.
    id: int  # noqa: A003
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
    # TODO: Check response model fields more carefully.
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

    # Sequence can be missing when Post model used inside PageBook model
    sequence: Optional[int] = None

    video_duration: Optional[float]
    generation_directives: Optional[GenerationDirectives]


class AIPost(BasePost):
    """Model that describes AI-generated posts.

    There is possibility that AI posts have the same fields as common posts,
    but premium account is needed to check it properly. So this model is
    actual for non-premium accounts.
    """
    # TODO: Check response model fields more carefully.
    updated_at: Optional[datetime]
    post_associated_id: Optional[int]
    generation_directives: Optional[AIGenerationDirectives]

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def normalize_datetime(cls, v) -> Optional[datetime]:  # noqa: D102
        return convert_ts_to_datetime(v)
