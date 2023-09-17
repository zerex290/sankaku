from datetime import datetime

import pytest

from sankaku.models import Book
from sankaku import types


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 403306032,
                "name_en": "ABCBook",
                "name_ja": None,
                "description": "",
                "description_en": None,
                "description_ja": None,
                "created_at": "2021-09-28 18:07",
                "updated_at": "2022-06-18 13:29",
                "author": {
                    "id": 2,
                    "name": "anonymous",
                    "avatar": "",
                    "avatar_rating": "s"
                },
                "is_public": False,
                "is_active": True,
                "is_flagged": False,
                "post_count": 50,
                "pages_count": 32,
                "visible_post_count": 25,
                "is_intact": True,
                "rating": "q",
                "reactions": [],
                "parent_id": None,
                "has_children": None,
                "is_rating_locked": False,
                "fav_count": 1350,
                "vote_count": 166,
                "total_score": 806,
                "comment_count": None,
                "tags": [],
                "post_tags": [],
                "artist_tags": [],
                "genre_tags": [],
                "is_favorited": False,
                "user_vote": None,
                "posts": [],
                "file_url": "URL",
                "sample_url": None,
                "preview_url": None,
                "cover_post": None,
                "reading": {
                    "current_page": 17,
                    "sequence": 15,
                    "post_id": 23423,
                    "series_id": None,
                    "created_at": "2023-04-22 20:00",
                    "updated_at": "2023-04-23 20:30",
                    "percent": 93
                },
                "is_premium": False,
                "is_pending": False,
                "is_raw": False,
                "is_trial": False,
                "redirect_to_signup": False,
                "locale": "en",
                "is_deleted": False,
                "cover_post_id": None,
                "name": "NAME",
                "parent_pool": None,
                "child_pools": None,
                "flagged_by_user": False,
                "prem_post_count": 0
            },
            dict(
                id=403306032,
                name_en="ABCBook",
                name_ja=None,
                description="",
                description_en=None,
                description_ja=None,
                created_at=datetime(2021, 9, 28, 18, 7),
                updated_at=datetime(2022, 6, 18, 13, 29),
                author=dict(
                    id=2,
                    name="anonymous",
                    avatar="",
                    avatar_rating=types.Rating.SAFE
                ),
                is_public=False,
                is_active=True,
                is_flagged=False,
                post_count=50,
                pages_count=32,
                visible_post_count=25,
                is_intact=True,
                rating=types.Rating.QUESTIONABLE,
                reactions=[],
                parent_id=None,
                has_children=None,
                is_rating_locked=False,
                fav_count=1350,
                vote_count=166,
                total_score=806,
                comment_count=None,
                tags=[],
                post_tags=[],
                artist_tags=[],
                genre_tags=[],
                is_favorited=False,
                user_vote=None,
                posts=[],
                file_url="URL",
                sample_url=None,
                preview_url=None,
                cover_post=None,
                reading=dict(  # Testing BookState model as well
                    current_page=17,
                    sequence=15,
                    post_id=23423,
                    series_id=None,
                    created_at=datetime(2023, 4, 22, 20, 0),
                    updated_at=datetime(2023, 4, 23, 20, 30),
                    percent=93
                ),
                is_premium=False,
                is_pending=False,
                is_raw=False,
                is_trial=False,
                redirect_to_signup=False,
                locale="en",
                is_deleted=False,
                cover_post_id=None,
                name="NAME",
                parent_pool=None,
                child_pools=None,
                flagged_by_user=False,
                prem_post_count=0
            )
        )
    ]
)
def test_book_model(data, expected):  # noqa: D103
    assert Book(**data).model_dump() == expected

