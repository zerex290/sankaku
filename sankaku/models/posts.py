from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

from sankaku import types
from .tags import PostTag


__all__ = ["Post", "AIPost"]


class Author(BaseModel):
    id: int
    name: str
    avatar: str
    avatar_rating: types.Rating


class GenerationDirectives(BaseModel):
    width: int
    height: int
    prompt: str
    batch_size: int
    batch_count: int
    sampling_steps: int
    negative_prompt: str


class BasePost(BaseModel):
    id: int
    created_at: dict[str, str | int] | datetime
    rating: types.Rating
    status: str
    author: Author
    file_url: Optional[str]
    preview_url: Optional[str]
    width: int
    height: int
    file_size: int
    extension: str = Field(alias="file_type")
    generation_directives: Optional[GenerationDirectives]
    md5: str
    tags: list[PostTag]

    @validator("created_at", pre=True)
    def convert_ts_to_datetime(cls, v) -> Optional[datetime]:  # noqa
        if isinstance(v, dict) and v.get("s"):
            return datetime.utcfromtimestamp(v["s"]).astimezone()
        return None

    @validator("extension", pre=True)
    def get_extension(cls, v) -> str:  # noqa
        return v.split("/")[1]

    @property
    def file_type(self) -> types.File:
        match self.extension:
            case "png" | "jpeg" | "webp":
                return types.File.IMAGE
            case "webm" | "mp4":
                return types.File.VIDEO
            case "gif":
                return types.File.GIF
            case _:
                raise ValueError(f"Undefined file extension [{self.extension}]")


class Post(BasePost):
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

    similar_posts: list["Post"] = []


class AIPost(BasePost):
    """
    There is possibility that AI posts have the same fields as common posts,
    but I don't have premium account to check it properly.
    This model is actual for non-premium accounts.
    """
    updated_at: Optional[dict[str, str | Optional[int]] | datetime]
    post_associated_id: Optional[int]

    @validator("created_at", "updated_at", pre=True)
    def convert_ts_to_datetime(cls, v) -> Optional[datetime]:  # noqa
        if isinstance(v, dict) and v.get("s"):
            return datetime.utcfromtimestamp(v["s"]).astimezone()
        return None
