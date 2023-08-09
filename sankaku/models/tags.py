from datetime import datetime
from typing import Optional, List

from pydantic import Field, field_validator

from sankaku import types
from sankaku.utils import convert_ts_to_datetime
from .base import SankakuResponseModel
from .users import Author


__all__ = ["PostTag", "PageTag", "Wiki", "WikiTag"]


class BaseTag(SankakuResponseModel):
    """Model that contains minimum amount of information that all tags have."""
    id: int  # noqa: A003
    name: str
    name_en: str
    name_ja: Optional[str]
    type: types.TagType  # noqa: A003
    post_count: int
    pool_count: int
    series_count: int
    rating: Optional[types.Rating]


class GenerationDirectivesTag(BaseTag):
    count: int
    tag_name: str = Field(alias="tagName")
    translations: List[str] = Field(alias="tag_translations")


class TagMixin(SankakuResponseModel):
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
    cached_related: Optional[List[int]] = Field(alias="cachedRelated")
    cached_related_expires_on: datetime = Field(alias="cachedRelatedExpiresOn")
    type: types.TagType = Field(alias="tagType")  # noqa: A003
    name_en: str = Field(alias="nameEn")
    name_ja: Optional[str] = Field(alias="nameJa")
    popularity_all: Optional[float] = Field(alias="scTagPopularityAll")
    quality_all: Optional[float] = Field(alias="scTagQualityAll")
    popularity_ero: Optional[float] = Field(alias="scTagPopularityEro")
    popularity_safe: Optional[float] = Field(alias="scTagPopularitySafe")
    quality_ero: Optional[float] = Field(alias="scTagQualityEro")
    quality_safe: Optional[float] = Field(alias="scTagQualitySafe")
    parent_tags: Optional[List[int]] = Field(alias="parentTags")
    child_tags: Optional[List[int]] = Field(alias="childTags")
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

    @field_validator("cached_related", "parent_tags", "child_tags", mode="before")
    @classmethod
    def flatten(cls, v) -> Optional[List[int]]:
        """Flatten nested lists into one."""
        if not v:
            return None
        tag_ids = v.split(",") if "," in v else v.split()
        try:
            return [int(tag_id) for tag_id in tag_ids]
        except ValueError:
            return None


class BaseTranslations(SankakuResponseModel):
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
    id: Optional[int] = None  # noqa: A003


class PageTag(PostTag):
    """Model that describes tags on tag page."""
    translations: List[PageTagTranslations]
    related_tags: List[NestedTag]
    child_tags: List[NestedTag]
    parent_tags: List[NestedTag]


class Wiki(SankakuResponseModel):
    """Model that describes wiki information for specific tag."""
    id: int  # noqa: A003
    title: str
    body: str
    created_at: datetime
    updated_at: Optional[datetime]
    author: Author = Field(alias="user")
    is_locked: bool
    version: int

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def normalize_datetime(cls, v) -> Optional[datetime]:  # noqa: D102
        return convert_ts_to_datetime(v)


class WikiTag(BaseTag, TagMixin):
    """Model that describes tag on wiki page."""
    related_tags: List[PostTag]
    child_tags: List[PostTag]
    parent_tags: List[PostTag]
    alias_tags: List[PostTag]
    implied_tags: List[PostTag]
    translations: List[WikiTagTranslations]
    wiki: Wiki
