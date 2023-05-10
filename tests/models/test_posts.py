from datetime import datetime, timezone

import pytest  # noqa

from sankaku.models import *
from sankaku import types


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 22144775,
                "rating": "q",
                "status": "active",
                "author": {
                    "id": 2,
                    "name": "anonymous",
                    "avatar": "URL",
                    "avatar_rating": "s"
                },
                "sample_url": "URL",
                "sample_width": 1399,
                "sample_height": 941,
                "preview_url": "URL",
                "preview_width": 300,
                "preview_height": 202,
                "file_url": "URL",
                "width": 5242,
                "height": 3525,
                "file_size": 8608194,
                "file_type": "image/jpeg",
                "created_at": {
                    "json_class": "Time",
                    "s": 1604093590,
                    "n": 0
                },
                "has_children": True,
                "has_comments": False,
                "has_notes": False,
                "is_favorited": False,
                "user_vote": None,
                "md5": "ab32849a455e9fca5e5fa24bd036d3e3",
                "parent_id": None,
                "change": 56235768,
                "fav_count": 92,
                "recommended_posts": -1,
                "recommended_score": 0,
                "vote_count": 20,
                "total_score": 94,
                "comment_count": None,
                "source": "",
                "in_visible_pool": False,
                "is_premium": False,
                "is_rating_locked": False,
                "is_note_locked": False,
                "is_status_locked": False,
                "redirect_to_signup": False,
                "sequence": None,
                "generation_directives": None,
                "tags": [],
                "video_duration": None
            },
            dict(
                id=22144775,
                rating=types.Rating.QUESTIONABLE,
                status="active",
                author=dict(
                    id=2,
                    name="anonymous",
                    avatar="URL",
                    avatar_rating=types.Rating.SAFE
                ),
                sample_url="URL",
                sample_width=1399,
                sample_height=941,
                preview_url="URL",
                preview_width=300,
                preview_height=202,
                file_url="URL",
                width=5242,
                height=3525,
                file_size=8608194,
                extension="jpeg",
                created_at=datetime(2020, 10, 30, 21, 33, 10).astimezone(),
                has_children=True,
                has_comments=False,
                has_notes=False,
                is_favorited=False,
                user_vote=None,
                md5="ab32849a455e9fca5e5fa24bd036d3e3",
                parent_id=None,
                change=56235768,
                fav_count=92,
                recommended_posts=-1,
                recommended_score=0,
                vote_count=20,
                total_score=94,
                comment_count=None,
                source="",
                in_visible_pool=False,
                is_premium=False,
                is_rating_locked=False,
                is_note_locked=False,
                is_status_locked=False,
                redirect_to_signup=False,
                sequence=None,
                generation_directives=None,
                tags=[],
                video_duration=None
            )
        )
    ]
)
def test_post_model(data, expected):
    assert Post(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 178711,
                "created_at": "2023-04-16T19:03:19.300Z",
                "post_id": 12345,
                "author": {
                    "id": 99123,
                    "name": "abcdef",
                    "avatar": "",
                    "avatar_rating": "q"
                },
                "body": "Hello, World!",
                "score": 3,
                "parent_id": None,
                "children": [],
                "deleted": False,
                "deleted_by": {},
                "updated_at": "2023-04-25T02:49:36.012Z",
                "can_reply": True,
                "reason": None
            },
            dict(
                id=178711,
                created_at=datetime(
                    2023, 4, 16, 19, 3, 19, 300000, tzinfo=timezone.utc
                ),
                post_id=12345,
                author=dict(
                    id=99123,
                    name="abcdef",
                    avatar="",
                    avatar_rating=types.Rating.QUESTIONABLE
                ),
                body="Hello, World!",
                score=3,
                parent_id=None,
                children=[],
                deleted=False,
                deleted_by={},
                updated_at=datetime(
                    2023, 4, 25, 2, 49, 36, 12000, tzinfo=timezone.utc
                ),
                can_reply=True,
                reason=None
            )
        )
    ]
)
def test_comment_model(data, expected):
    assert Comment(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 131,
                "created_at": {
                    "json_class": "Time",
                    "s": 1675452087,
                    "n": 0
                },
                "updated_at": {
                    "json_class": "Time",
                    "s": None,
                    "n": 0
                },
                "rating": "s",
                "status": "active",
                "author": {
                    "id": 1,
                    "name": "System",
                    "avatar": "URL",
                    "avatar_rating": "q"
                },
                "file_url": "URL",
                "preview_url": "URL",
                "width": 512,
                "height": 512,
                "file_size": 331855,
                "file_type": "image/png",
                "post_associated_id": None,
                "generation_directives": {
                    "width": 512,
                    "height": 512,
                    "prompt": "tatami",
                    "batch_size": 50,
                    "batch_count": 1,
                    "sampling_steps": 50,
                    "negative_prompt": "bad quality"
                },
                "md5": "93b5f88ffe0b9ec49dd2d0b0289fd3ff",
                "tags": []
            },
            dict(
                id=131,
                created_at=datetime(2023, 2, 3, 19, 21, 27).astimezone(),
                updated_at=None,
                rating=types.Rating.SAFE,
                status="active",
                author=dict(
                    id=1,
                    name="System",
                    avatar="URL",
                    avatar_rating="q"
                ),
                file_url="URL",
                preview_url="URL",
                width=512,
                height=512,
                file_size=331855,
                extension="png",
                post_associated_id=None,
                generation_directives=dict(
                    width=512,
                    height=512,
                    prompt="tatami",
                    batch_size=50,
                    batch_count=1,
                    sampling_steps=50,
                    negative_prompt="bad quality"
                ),
                md5="93b5f88ffe0b9ec49dd2d0b0289fd3ff",
                tags=[]
            )
        )
    ]
)
def test_ai_post_model(data, expected):
    assert AIPost(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.
