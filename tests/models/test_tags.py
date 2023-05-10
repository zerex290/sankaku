from datetime import datetime, timezone

import pytest  # noqa

from sankaku.models import *
from sankaku import types


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 1129497,
                "name_en": "hololive",
                "name_ja": "ホロライブ",
                "type": 3,
                "count": 182184,
                "post_count": 182184,
                "pool_count": 549,
                "series_count": 0,
                "locale": "en",
                "rating": "s",
                "version": 1,
                "tagName": "hololive",
                "total_post_count": 182184,
                "total_pool_count": 549,
                "name": "hololive"
            },
            dict(
                id=1129497,
                name_en="hololive",
                name_ja="ホロライブ",
                type=types.Tag(3),
                count=182184,
                post_count=182184,
                pool_count=549,
                series_count=0,
                locale="en",
                rating=types.Rating.SAFE,
                version=1,
                tag_name="hololive",
                total_post_count=182184,
                total_pool_count=549,
                name="hololive"
            )
        ),
        (
            {
                "id": 1497,
                "name_en": "qwerty",
                "name_ja": None,
                "type": 5,
                "count": 182184,
                "post_count": 182184,
                "pool_count": 549,
                "series_count": 0,
                "locale": "en",
                "rating": None,
                "version": None,
                "tagName": "hololive",
                "total_post_count": 182184,
                "total_pool_count": 549,
                "name": "hololive"
            },
            dict(
                id=1497,
                name_en="qwerty",
                name_ja=None,
                type=types.Tag.GENRE,
                count=182184,
                post_count=182184,
                pool_count=549,
                series_count=0,
                locale="en",
                rating=None,
                version=None,
                tag_name="hololive",
                total_post_count=182184,
                total_pool_count=549,
                name="hololive"
            )
        )
    ]
)
def test_post_tag_model(data, expected):
    assert PostTag(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 34240,
                "name_en": "female",
                "name_ja": "女性",
                "type": 0,
                "count": 10821550,
                "post_count": 10821550,
                "pool_count": 97939,
                "series_count": 0,
                "locale": "en",
                "rating": "s",
                "version": 1,
                "translations": [
                    {
                        "rootId": 34240,
                        "lang": "ja",
                        "translation": "女性"
                    }
                ],
                "tagName": "female",
                "total_post_count": 10821550,
                "total_pool_count": 97939,
                "name": "female",
                "related_tags": [],
                "child_tags": [
                    {
                        "name": "yuri",
                        "postCount": 337420,
                        "cachedRelated": "209,3273,104803,462,3199",
                        "cachedRelatedExpiresOn": "2023-07-06T12:36:01.109Z",
                        "tagType": 5,
                        "nameEn": "yuri",
                        "nameJa": "百合",
                        "scTagPopularityAll": 0.00072376704,
                        "scTagQualityAll": 26.17608,
                        "scTagPopularityEro": 0.0011845038,
                        "scTagPopularitySafe": 0.0003316918,
                        "scTagQualityEro": 25.622679,
                        "scTagQualitySafe": 6.277924,
                        "parentTags": "34240 104803",
                        "childTags": "159972 674372 914037 920061",
                        "poolCount": 21530,
                        "rating": "q",
                        "version": 363,
                        "premPostCount": 0,
                        "nonPremPostCount": 290179,
                        "premPoolCount": 0,
                        "nonPremPoolCount": 21467,
                        "seriesCount": 0,
                        "premSeriesCount": 0,
                        "nonPremSeriesCount": 0,
                        "isTrained": True,
                        "child": 209,
                        "parent": 34240,
                        "id": 209
                    }
                ],
                "parent_tags": [
                    {
                        "name": "femdom",
                        "postCount": 92372,
                        "cachedRelated": "",
                        "cachedRelatedExpiresOn": "2023-07-06T17:06:17.902Z",
                        "tagType": 5,
                        "nameEn": "femdom",
                        "nameJa": None,
                        "scTagPopularityAll": None,
                        "scTagQualityAll": None,
                        "scTagPopularityEro": None,
                        "scTagPopularitySafe": None,
                        "scTagQualityEro": None,
                        "scTagQualitySafe": None,
                        "parentTags": None,
                        "childTags": None,
                        "poolCount": 18729,
                        "rating": None,
                        "version": None,
                        "premPostCount": 0,
                        "nonPremPostCount": 74602,
                        "premPoolCount": 0,
                        "nonPremPoolCount": 18724,
                        "seriesCount": 0,
                        "premSeriesCount": 0,
                        "nonPremSeriesCount": 0,
                        "isTrained": True,
                        "child": 3386,
                        "parent": 34240,
                        "id": 3386
                    }
                ]
            },
            dict(
                id=34240,
                name_en="female",
                name_ja="女性",
                type=types.Tag.GENERAL,
                count=10821550,
                post_count=10821550,
                pool_count=97939,
                series_count=0,
                locale="en",
                rating=types.Rating.SAFE,
                version=1,
                translations=[
                    dict(
                        root_id=34240,
                        lang="ja",
                        translation="女性"
                    )
                ],
                tag_name="female",
                total_post_count=10821550,
                total_pool_count=97939,
                name="female",
                related_tags=[],
                child_tags=[
                    dict(
                        name="yuri",
                        post_count=337420,
                        cached_related=[209, 3273, 104803, 462, 3199],
                        cached_related_expires_on=datetime(
                            2023, 7, 6, 12, 36, 1, 109000, tzinfo=timezone.utc
                        ),
                        type=types.Tag(5),
                        name_en="yuri",
                        name_ja="百合",
                        popularity_all=0.00072376704,
                        quality_all=26.17608,
                        popularity_ero=0.0011845038,
                        popularity_safe=0.0003316918,
                        quality_ero=25.622679,
                        quality_safe=6.277924,
                        parent_tags=[34240, 104803],
                        child_tags=[159972, 674372, 914037, 920061],
                        pool_count=21530,
                        rating=types.Rating.QUESTIONABLE,
                        version=363,
                        premium_post_count=0,
                        non_premium_post_count=290179,
                        premium_pool_count=0,
                        non_premium_pool_count=21467,
                        series_count=0,
                        premium_series_count=0,
                        non_premium_series_count=0,
                        is_trained=True,
                        child=209,
                        parent=34240,
                        id=209
                    )
                ],
                parent_tags=[
                    dict(
                        name="femdom",
                        post_count=92372,
                        cached_related=None,
                        cached_related_expires_on=datetime(
                            2023, 7, 6, 17, 6, 17, 902000, tzinfo=timezone.utc
                        ),
                        type=types.Tag(5),
                        name_en="femdom",
                        name_ja=None,
                        popularity_all=None,
                        quality_all=None,
                        popularity_ero=None,
                        popularity_safe=None,
                        quality_ero=None,
                        quality_safe=None,
                        parent_tags=None,
                        child_tags=None,
                        pool_count=18729,
                        rating=None,
                        version=None,
                        premium_post_count=0,
                        non_premium_post_count=74602,
                        premium_pool_count=0,
                        non_premium_pool_count=18724,
                        series_count=0,
                        premium_series_count=0,
                        non_premium_series_count=0,
                        is_trained=True,
                        child=3386,
                        parent=34240,
                        id=3386
                    )
                ]
            )
        )
    ]
)
def test_page_tag_model(data, expected):
    assert PageTag(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 100,
                "name": "randosel",
                "name_en": "randosel",
                "name_ja": "ランドセル",
                "tagName": "randosel",
                "type": 0,
                "count": 24071,
                "post_count": 24071,
                "pool_count": 925,
                "series_count": 0,
                "rating": "s",
                "related_tags": [],
                "child_tags": [],
                "parent_tags": [],
                "alias_tags": [],
                "implied_tags": [],
                "translations": [],
                "total_post_count": 10,
                "total_pool_count": 5,
                "wiki": {
                    "id": 4,
                    "title": "randosel",
                    "body": "The Japanese elementary school backpack.",
                    "created_at": {
                        "json_class": "Time",
                        "s": 1226516733,
                        "n": 0
                    },
                    "updated_at": {
                        "json_class": "Time",
                        "s": None,
                        "n": 0
                    },
                    "user": {
                        "id": 483218,
                        "name": "SpaceEntity",
                        "avatar": "URL",
                        "avatar_rating": "s"
                    },
                    "is_locked": False,
                    "version": 6
                }
            },
            dict(
                id=100,
                name="randosel",
                name_en="randosel",
                name_ja="ランドセル",
                tag_name="randosel",
                type=types.Tag.GENERAL,
                count=24071,
                post_count=24071,
                pool_count=925,
                series_count=0,
                rating=types.Rating("s"),
                related_tags=[],
                child_tags=[],
                parent_tags=[],
                alias_tags=[],
                implied_tags=[],
                translations=[],
                total_post_count=10,
                total_pool_count=5,
                wiki=dict(
                    id=4,
                    title="randosel",
                    body="The Japanese elementary school backpack.",
                    created_at=datetime(2008, 11, 12, 19, 5, 33).astimezone(),
                    updated_at=None,
                    author=dict(
                        id=483218,
                        name="SpaceEntity",
                        avatar="URL",
                        avatar_rating=types.Rating.SAFE
                    ),
                    is_locked=False,
                    version=6
                )
            )
        )
    ]
)
def test_wiki_tag_model(data, expected):
    assert WikiTag(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.
