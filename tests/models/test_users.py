from datetime import datetime, timezone

import pytest  # noqa

from sankaku.models import *
from sankaku import types


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 49321,
                "name": "afern",
                "avatar": "",
                "avatar_rating": "q"
            },
            dict(
                id=49321,
                name="afern",
                avatar="",
                avatar_rating=types.Rating.QUESTIONABLE
            )
        )
    ]
)
def test_author_model(data, expected):
    assert Author(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "last_logged_in_at": "2023-05-09T03:07:39.650Z",
                "favorite_count": 0,
                "post_favorite_count": 0,
                "pool_favorite_count": 0,
                "vote_count": 16,
                "post_vote_count": 16,
                "pool_vote_count": 0,
                "recommended_posts_for_user": "200",
                "subscriptions": ["a", "b"],
                "id": 49276,
                "name": "reichan",
                "level": 45,
                "upload_limit": 1000,
                "created_at": "2013-03-02T17:31:47.688Z",
                "favs_are_private": False,
                "avatar_url": "URL",
                "avatar_rating": "s",
                "post_upload_count": 2370825,
                "pool_upload_count": 0,
                "comment_count": 1,
                "post_update_count": 3297994,
                "note_update_count": 0,
                "wiki_update_count": 0,
                "forum_post_count": 0,
                "pool_update_count": 0,
                "series_update_count": 0,
                "tag_update_count": 0,
                "artist_update_count": 0,
                "show_popup_version": 1,
                "credits": 0,
                "credits_subs": 0,
                "is_ai_beta": False
            },
            dict(
                last_logged_in_at=datetime(
                    2023, 5, 9, 3, 7, 39, 650000, tzinfo=timezone.utc
                ),
                favorite_count=0,
                post_favorite_count=0,
                pool_favorite_count=0,
                vote_count=16,
                post_vote_count=16,
                pool_vote_count=0,
                recommended_posts_for_user=200,
                subscriptions=["a", "b"],
                id=49276,
                name="reichan",
                level=45,
                upload_limit=1000,
                created_at=datetime(
                    2013, 3, 2, 17, 31, 47, 688000, tzinfo=timezone.utc
                ),
                favs_are_private=False,
                avatar="URL",
                avatar_rating=types.Rating.SAFE,
                post_upload_count=2370825,
                pool_upload_count=0,
                comment_count=1,
                post_update_count=3297994,
                note_update_count=0,
                wiki_update_count=0,
                forum_post_count=0,
                pool_update_count=0,
                series_update_count=0,
                tag_update_count=0,
                artist_update_count=0,
                show_popup_version=1,
                credits=0,
                credits_subs=0,
                is_ai_beta=False
            )
        ),
        (
            {
                "id": 49276,
                "name": "reichan",
                "level": 45,
                "upload_limit": 1000,
                "created_at": "2013-03-02T17:31:47.688Z",
                "favs_are_private": False,
                "avatar_url": "URL",
                "avatar_rating": "s",
                "post_upload_count": 2370825,
                "pool_upload_count": 0,
                "comment_count": 1,
                "post_update_count": 3297994,
                "note_update_count": 0,
                "wiki_update_count": 0,
                "forum_post_count": 0,
                "pool_update_count": 0,
                "series_update_count": 0,
                "tag_update_count": 0,
                "artist_update_count": 0,
                "show_popup_version": 1,
                "credits": 0,
                "credits_subs": 0,
                "is_ai_beta": False
            },
            dict(
                last_logged_in_at=None,
                favorite_count=None,
                post_favorite_count=None,
                pool_favorite_count=None,
                vote_count=None,
                post_vote_count=None,
                pool_vote_count=None,
                recommended_posts_for_user=None,
                subscriptions=[],
                id=49276,
                name="reichan",
                level=45,
                upload_limit=1000,
                created_at=datetime(
                    2013, 3, 2, 17, 31, 47, 688000, tzinfo=timezone.utc
                ),
                favs_are_private=False,
                avatar="URL",
                avatar_rating=types.Rating.SAFE,
                post_upload_count=2370825,
                pool_upload_count=0,
                comment_count=1,
                post_update_count=3297994,
                note_update_count=0,
                wiki_update_count=0,
                forum_post_count=0,
                pool_update_count=0,
                series_update_count=0,
                tag_update_count=0,
                artist_update_count=0,
                show_popup_version=1,
                credits=0,
                credits_subs=0,
                is_ai_beta=False
            )
        )
    ]
)
def test_user_model(data, expected):
    assert User(**data) == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (
            {
                "id": 17488,
                "name": "ABC",
                "avatar_url": "",
                "avatar_rating": "e",
                "last_logged_in_at": "2022-04-09T17:31:47.658Z",
                "favorite_count": 143,
                "post_favorite_count": 198,
                "pool_favorite_count": 9,
                "vote_count": 27,
                "post_vote_count": 2,
                "pool_vote_count": 6,
                "recommended_posts_for_user": 13,
                "subscriptions": [],
                "level": 20,
                "upload_limit": 381,
                "created_at": "2015-07-08T23:57:16.723Z",
                "favs_are_private": True,
                "post_upload_count": 0,
                "pool_upload_count": 0,
                "comment_count": 0,
                "post_update_count": 0,
                "note_update_count": 0,
                "wiki_update_count": 0,
                "forum_post_count": 0,
                "pool_update_count": 0,
                "series_update_count": 0,
                "tag_update_count": 0,
                "artist_update_count": 0,
                "show_popup_version": 1,
                "credits": 0,
                "credits_subs": 0,
                "is_ai_beta": False,
                "email": "ABCDEFU@eksdee.xyz",
                "hide_ads": False,
                "subscription_level": 0,
                "filter_content": False,
                "has_mail": False,
                "receive_dmails": True,
                "email_verification_status": "verified",
                "is_verified": True,
                "verifications_count": 2,
                "blacklist_is_hidden": True,
                "blacklisted_tags": [
                    ["loli"],
                    ["shota"],
                    ["yaoi"]
                ],
                "blacklisted": [
                    "loli\nshota\nyaoi"
                ],
                "mfa_method": 1
            },
            dict(
                id=17488,
                name="ABC",
                avatar="",
                avatar_rating=types.Rating.EXPLICIT,
                last_logged_in_at=datetime(
                    2022, 4, 9, 17, 31, 47, 658000, tzinfo=timezone.utc
                ),
                favorite_count=143,
                post_favorite_count=198,
                pool_favorite_count=9,
                vote_count=27,
                post_vote_count=2,
                pool_vote_count=6,
                recommended_posts_for_user=13,
                subscriptions=[],
                level=20,
                upload_limit=381,
                created_at=datetime(
                    2015, 7, 8, 23, 57, 16, 723000, tzinfo=timezone.utc
                ),
                favs_are_private=True,
                post_upload_count=0,
                pool_upload_count=0,
                comment_count=0,
                post_update_count=0,
                note_update_count=0,
                wiki_update_count=0,
                forum_post_count=0,
                pool_update_count=0,
                series_update_count=0,
                tag_update_count=0,
                artist_update_count=0,
                show_popup_version=1,
                credits=0,
                credits_subs=0,
                is_ai_beta=False,
                email="ABCDEFU@eksdee.xyz",
                hide_ads=False,
                subscription_level=0,
                filter_content=False,
                has_mail=False,
                receive_dmails=True,
                email_verification_status="verified",
                is_verified=True,
                verifications_count=2,
                blacklist_is_hidden=True,
                blacklisted_tags=["loli", "shota", "yaoi"],
                blacklisted=["loli\nshota\nyaoi"],
                mfa_method=1
            )

        )
    ]
)
def test_extended_user_model(data, expected):
    assert ExtendedUser(**data).dict() == expected
    # Pydantic converts Model to dict before comparing,
    # So there is no need in calling model '.dict()' method.
