from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

from sankaku import types
from sankaku.utils import convert_ts_to_datetime
from .users import Author


__all__ = ["PostTag", "PageTag", "Wiki", "WikiTag"]


class BaseTag(BaseModel):
    """Model that contains minimum amount of information that all tags have."""
    id: int
    name: str
    name_en: str
    name_ja: Optional[str]
    type: types.TagType
    post_count: int
    pool_count: int
    series_count: int
    rating: Optional[types.Rating]


class TagMixin(BaseModel):
    """Additional data that certain tags have."""
    count: int
    tag_name: str = Field(alias="tagName")
    total_post_count: int
    total_pool_count: int


class PostTag(BaseTag, TagMixin):
    """Model that describes tags related to posts."""
    locale: Optional[str]
    version: Optional[int]


class NestedTag(BaseTag):
    """Model that describes tags with specific relation to certain tag on tag page."""
    post_count: int = Field(alias="postCount")
    cached_related: Optional[list[int]] = Field(alias="cachedRelated")
    cached_related_expires_on: datetime = Field(alias="cachedRelatedExpiresOn")
    type: types.TagType = Field(alias="tagType")
    name_en: str = Field(alias="nameEn")
    name_ja: Optional[str] = Field(alias="nameJa")
    popularity_all: Optional[float] = Field(alias="scTagPopularityAll")
    quality_all: Optional[float] = Field(alias="scTagQualityAll")
    popularity_ero: Optional[float] = Field(alias="scTagPopularityEro")
    popularity_safe: Optional[float] = Field(alias="scTagPopularitySafe")
    quality_ero: Optional[float] = Field(alias="scTagQualityEro")
    quality_safe: Optional[float] = Field(alias="scTagQualitySafe")
    parent_tags: Optional[list[int]] = Field(alias="parentTags")
    child_tags: Optional[list[int]] = Field(alias="childTags")
    pool_count: int = Field(alias="poolCount")
    premium_post_count: int = Field(alias="premPostCount")
    non_premium_post_count: int = Field(alias="nonPremPostCount")
    premium_pool_count: int = Field(alias="premPoolCount")
    non_premium_pool_count: int = Field(alias="nonPremPoolCount")
    series_count: int = Field(alias="seriesCount")
    premium_series_count: int = Field(alias="premSeriesCount")
    non_premium_series_count: int = Field(alias="nonPremSeriesCount")
    is_trained: bool = Field(alias="isTrained")
    child: int
    parent: int
    version: Optional[int]

    @validator("cached_related", "parent_tags", "child_tags", pre=True)
    def flatten(cls, v) -> Optional[list[int]]:  # noqa
        """Flatten nested lists into one."""
        if not v:
            return None
        tag_ids = v.split(",") if "," in v else v.split()
        try:
            return [int(tag_id) for tag_id in tag_ids]
        except ValueError:
            return None


class BaseTranslations(BaseModel):
    """Model that contain minimum information about tag translations."""
    lang: str
    translation: str


class PageTagTranslations(BaseTranslations):
    """Model that describes page tag translations."""
    root_id: int = Field(alias="rootId")


class WikiTagTranslations(BaseTranslations):
    """Model that describes wiki tag translations."""
    status: int
    opacity: float


class PageTag(PostTag):
    """Model that describes tags on tag page."""
    translations: list[PageTagTranslations]
    related_tags: list[NestedTag]
    child_tags: list[NestedTag]
    parent_tags: list[NestedTag]


class Wiki(BaseModel):
    """Model that describes wiki information for specific tag."""
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: Optional[datetime]
    author: Author = Field(alias="user")
    is_locked: bool
    version: int

    # Validators
    _normalize_datetime = (
        validator("created_at", "updated_at", pre=True, allow_reuse=True)
        (convert_ts_to_datetime)
    )


class WikiTag(BaseTag, TagMixin):
    """Model that describes tag on wiki page."""
    related_tags: list[PostTag]
    child_tags: list[PostTag]
    parent_tags: list[PostTag]
    alias_tags: list[PostTag]
    implied_tags: list[PostTag]
    translations: list[WikiTagTranslations]
    wiki: Wiki
