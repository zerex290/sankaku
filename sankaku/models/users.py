from datetime import datetime
from typing import Optional, List

from pydantic import Field, field_validator

from sankaku import types
from .base import SankakuResponseModel


__all__ = ["Author", "User", "ExtendedUser"]


class BaseUser(SankakuResponseModel):
    """User profile with a minimum amount of information."""
    id: int  # noqa: A003
    name: str
    avatar: str
    avatar_rating: types.Rating


class Author(BaseUser):
    """Model that describes users who are the authors of posts or wiki pages."""


class User(BaseUser):
    """User profile model for any user that has an account on website."""
    level: int
    upload_limit: int
    created_at: datetime
    favs_are_private: bool
    avatar: str = Field(alias="avatar_url")
    post_upload_count: int
    pool_upload_count: int
    comment_count: int
    post_update_count: int
    note_update_count: int
    wiki_update_count: int
    forum_post_count: int
    pool_update_count: int
    series_update_count: int
    tag_update_count: int
    artist_update_count: int

    # The following fields can be missing in server JSON response
    last_logged_in_at: Optional[datetime] = None
    favorite_count: Optional[int] = None
    post_favorite_count: Optional[int] = None
    pool_favorite_count: Optional[int] = None
    vote_count: Optional[int] = None
    post_vote_count: Optional[int] = None
    pool_vote_count: Optional[int] = None
    recommended_posts_for_user: Optional[int] = None
    subscriptions: List[str] = []


class ExtendedUser(User):
    """Profile of the currently logged-in user."""
    email: str
    hide_ads: bool
    subscription_level: int
    filter_content: bool
    has_mail: bool
    receive_dmails: bool
    email_verification_status: str
    is_verified: bool
    verifications_count: int
    blacklist_is_hidden: bool
    blacklisted_tags: List[str]
    blacklisted: List[str]
    mfa_method: int
    show_popup_version: Optional[int]
    credits: Optional[int]  # noqa A003
    credits_subs: Optional[int]

    @field_validator("blacklisted_tags", mode="before")
    @classmethod
    def flatten_blacklisted_tags(cls, v) -> List[str]:
        """Flatten nested lists into one."""
        return [tag[0] for tag in v]
