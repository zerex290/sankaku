from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

from sankaku import types


__all__ = ["PostTag", "Tag"]


class BaseTag(BaseModel):
    id: int
    name: str
    name_en: str
    name_ja: Optional[str]
    type: types.Tag
    post_count: int
    pool_count: int
    series_count: int
    rating: Optional[types.Rating]
    version: Optional[int]


class PostTag(BaseTag):
    count: int
    locale: str
    tag_name: str = Field(alias="tagName")
    total_post_count: int
    total_pool_count: int


class NestedTag(BaseTag):
    post_count: int = Field(alias="postCount")
    cached_related: Optional[str | list[int]] = Field(alias="cachedRelated")
    cached_related_expires_on: datetime = Field(alias="cachedRelatedExpiresOn")
    type: types.Tag = Field(alias="tagType")
    name_en: str = Field(alias="nameEn")
    name_ja: Optional[str] = Field(alias="nameJa")
    popularity_all: Optional[float] = Field(alias="scTagPopularityAll")
    quality_all: Optional[float] = Field(alias="scTagQualityAll")
    popularity_ero: Optional[float] = Field(alias="scTagPopularityEro")
    popularity_safe: Optional[float] = Field(alias="scTagPopularitySafe")
    quality_ero: Optional[float] = Field(alias="scTagQualityEro")
    quality_safe: Optional[float] = Field(alias="scTagQualitySafe")
    parent_tags: Optional[str | list[int]] = Field(alias="parentTags")
    child_tags: Optional[str | list[int]] = Field(alias="childTags")
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

    @validator("cached_related", "parent_tags", "child_tags", pre=True)
    def flatten(cls, v) -> Optional[list[int]]:  # noqa
        if v is None:
            return None
        elif "," in v:
            t_ids = v.split(",")
        else:
            t_ids = v.split()
        try:
            return [int(t_id) for t_id in t_ids]
        except ValueError:
            return None


class Translations(BaseModel):
    root_id: int = Field(alias="rootId")
    lang: str
    translation: str


class Tag(PostTag):
    translations: list[Translations]
    related_tags: list[NestedTag]
    child_tags: list[NestedTag]
    parent_tags: list[NestedTag]
