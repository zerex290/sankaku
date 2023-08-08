from datetime import datetime

import pytest

from sankaku import errors, models as mdl, types
from sankaku.clients import SankakuClient


class TestBaseClient:
    @pytest.mark.parametrize(
        ["data", "expected"],
        [
            ({"access_token": "invalid"}, errors.AuthorizationError),
            ({"login": "invalid", "password": "invalid"}, errors.AuthorizationError),
            ({}, errors.SankakuError)
        ]
    )
    async def test_login_with_invalid_data(  # noqa: D102
        self,
        nlclient: SankakuClient,
        data,
        expected
    ):
        with pytest.raises(expected):
            await nlclient.login(**data)

    async def test_login_with_valid_data(self, lclient: SankakuClient):  # noqa: D102
        assert isinstance(lclient.profile, mdl.ExtendedUser)


class TestPostClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await nlclient.browse_posts(1).__anext__(), mdl.Post)

    @pytest.mark.parametrize(
        ["file_type", "video_duration", "expected"],
        [(types.FileType.IMAGE, [1, 60], errors.VideoDurationError)]
    )
    async def test_browse_with_incompatible_args(
        self,
        nlclient: SankakuClient,
        file_type,
        video_duration,
        expected
    ):
        """Case when arguments are incompatible."""
        with pytest.raises(expected):
            await nlclient.browse_posts(
                1,
                file_type=file_type,
                video_duration=video_duration
            ).__anext__()

    @pytest.mark.parametrize(
        [
            "order", "date", "rating",
            "threshold", "hide_posts_in_books",
            "file_size", "file_type",
            "video_duration", "recommended_for",
            "favorited_by", "tags",
            "added_by", "voted"

        ],
        [
            (
                types.PostOrder.POPULARITY, None, None,
                None, "always",
                None, None,
                None, None,
                None, None,
                None, None
            ),
            (
                types.PostOrder.QUALITY, None, types.Rating.EXPLICIT,
                None, "in-larger-tags",
                None, types.FileType.IMAGE,
                None, "Nigredo",
                None, None,
                None, None
            ),
            (
                types.PostOrder.DATE, [datetime(2018, 6, 16)], None,
                4, None,
                None, types.FileType.VIDEO,
                [1, 900], None,
                None, ["animated"],
                ["anonymous"], "Nigredo"
            ),
            (
                types.PostOrder.DATE, None, None,
                4, None,
                types.FileSize.LARGE, None,
                None, None,
                "Nigredo", ["female", "solo"],
                None, None
            )
        ]
    )
    async def test_browse_with_random_args(  # noqa: D102
        self,
        lclient: SankakuClient,
        order,
        date,
        rating,
        threshold,
        hide_posts_in_books,
        file_size,
        file_type,
        video_duration,
        recommended_for,
        favorited_by,
        tags,
        added_by,
        voted
    ):
        post = await lclient.browse_posts(
            1,
            order=order,
            date=date,
            rating=rating,
            threshold=threshold,
            hide_posts_in_books=hide_posts_in_books,
            file_size=file_size,
            file_type=file_type,
            video_duration=video_duration,
            recommended_for=recommended_for,
            favorited_by=favorited_by,
            tags=tags,
            added_by=added_by,
            voted=voted
        ).__anext__()
        assert isinstance(post, mdl.Post)

    async def test_get_favorited_posts_unauthorized(self, nlclient: SankakuClient):  # noqa: D102, E501
        with pytest.raises(errors.LoginRequirementError):
            await nlclient.get_favorited_posts(1).__anext__()

    async def test_get_favorited_posts_authorized(self, lclient: SankakuClient):  # noqa: D102, E501
        assert isinstance(await lclient.get_favorited_posts(1).__anext__(), mdl.Post)

    async def test_get_top_posts(self, nlclient: SankakuClient):  # noqa: D102
        assert isinstance(await nlclient.get_top_posts(1).__anext__(), mdl.Post)

    async def test_get_popular_posts(self, nlclient: SankakuClient):  # noqa: D102
        assert isinstance(await nlclient.get_popular_posts(1).__anext__(), mdl.Post)

    async def test_get_recommended_posts_unauthorized(self, nlclient: SankakuClient):  # noqa: D102, E501
        with pytest.raises(errors.LoginRequirementError):
            await nlclient.get_recommended_posts(1).__anext__()

    async def test_get_recommended_posts_authorized(self, lclient: SankakuClient):  # noqa: D102, E501
        assert isinstance(await lclient.get_recommended_posts(1).__anext__(), mdl.Post)

    @pytest.mark.parametrize(["post_id"], [(32948875,)])
    async def test_get_similar_posts(self, lclient: SankakuClient, post_id):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_similar_posts(1, post_id=post_id).__anext__(),
            mdl.Post
        )

    @pytest.mark.parametrize(["post_id"], [(33108291,)])
    async def test_get_post_comments(self, lclient: SankakuClient, post_id):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_post_comments(post_id).__anext__(),
            mdl.Comment
        )

    @pytest.mark.parametrize(["post_id"], [(32948875,), (33108291,)])
    async def test_get_post(self, nlclient: SankakuClient, post_id):  # noqa: D102
        post = await nlclient.get_post(post_id)
        assert isinstance(post, mdl.Post)

    async def test_get_non_existent_post(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(errors.PageNotFoundError):
            await lclient.get_post(-10_000)

    async def test_create_post(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(NotImplementedError):
            await lclient.create_post()


class TestAIClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await nlclient.browse_ai_posts(1).__anext__(), mdl.AIPost)

    @pytest.mark.parametrize(["post_id"], [(123,), (1721,)])
    async def test_get_ai_post(self, nlclient: SankakuClient, post_id):  # noqa: D102
        post = await nlclient.get_ai_post(post_id,)
        assert isinstance(post, mdl.AIPost)

    async def test_get_non_existent_ai_post(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(errors.PageNotFoundError):
            await lclient.get_ai_post(-10_000)

    async def test_create_ai_post(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(NotImplementedError):
            await lclient.create_ai_post()


class TestTagClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await nlclient.browse_tags(1).__anext__(), mdl.PageTag)

    @pytest.mark.parametrize(
        [
            "tag_type", "order",
            "rating", "max_post_count",
            "sort_parameter", "sort_direction"
        ],
        [
            (
                types.TagType.CHARACTER, None,
                types.Rating.SAFE, None,
                None, types.SortDirection.DESC
            ),
            (
                types.TagType.COPYRIGHT, types.TagOrder.POPULARITY,
                types.Rating.QUESTIONABLE, None,
                None, types.SortDirection.ASC
            ),
            (
                None, None,
                types.Rating.QUESTIONABLE, 2_537_220,
                types.SortParameter.NAME, types.SortDirection.ASC
            )
        ]
    )
    async def test_browse_with_random_args(  # noqa: D102
        self,
        lclient: SankakuClient,
        tag_type,
        order,
        rating,
        max_post_count,
        sort_parameter,
        sort_direction
    ):
        tag = await lclient.browse_tags(
            1,
            tag_type=tag_type,
            order=order,
            rating=rating,
            max_post_count=max_post_count,
            sort_parameter=sort_parameter,
            sort_direction=sort_direction
        ).__anext__()
        assert isinstance(tag, mdl.PageTag)

    @pytest.mark.parametrize(["name_or_id"], [("animated",), (100,)])
    async def test_get_tag(self, lclient: SankakuClient, name_or_id):  # noqa: D102
        wiki_tag = await lclient.get_tag(name_or_id)
        assert isinstance(wiki_tag, mdl.WikiTag)

    async def test_get_non_existent_tag(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(errors.PageNotFoundError):
            await lclient.get_tag(-10_000)


class TestBookClient:
    async def test_browse_default(self, nlclient: SankakuClient):  # noqa: D102
        assert isinstance(await nlclient.browse_books(1).__anext__(), mdl.PageBook)

    @pytest.mark.parametrize(
        [
            "order", "rating", "recommended_for",
            "favorited_by", "tags", "added_by",
            "voted"
        ],
        [
            (
                types.BookOrder.RANDOM, types.Rating.EXPLICIT, "reichan",
                None, None, None, None
            ),
            (
                types.BookOrder.POPULARITY, None, None,
                "Nigredo", None, None, "Nigredo"
            ),
            (
                None, None, None,
                None, ["genshin_impact"], ["yanququ"], None
            )
        ]
    )
    async def test_browse_with_random_args(  # noqa: D102
        self,
        lclient: SankakuClient,
        order,
        rating,
        recommended_for,
        favorited_by,
        tags,
        added_by,
        voted
    ):
        book = await lclient.browse_books(
            1,
            order=order,
            rating=rating,
            recommended_for=recommended_for,
            favorited_by=favorited_by,
            tags=tags,
            added_by=added_by,
            voted=voted
        ).__anext__()
        assert isinstance(book, mdl.PageBook)

    async def test_favorited_books_unauthorized(self, nlclient: SankakuClient):  # noqa: D102, E501
        with pytest.raises(errors.LoginRequirementError):
            await nlclient.get_favorited_books(1).__anext__()

    async def test_favorited_books_authorized(self, lclient: SankakuClient):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_favorited_books(1).__anext__(),
            mdl.PageBook
        )

    async def test_recommended_books_unauthorized(self, nlclient: SankakuClient):  # noqa: D102, E501
        with pytest.raises(errors.LoginRequirementError):
            await nlclient.get_recommended_books(1).__anext__()

    async def test_recommended_books_authorized(self, lclient: SankakuClient):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_recommended_books(1).__anext__(),
            mdl.PageBook
        )

    async def test_recently_read_books_unauthorized(self, nlclient: SankakuClient):  # noqa: D102, E501
        with pytest.raises(errors.LoginRequirementError):
            await nlclient.get_recently_read_books(1).__anext__()

    async def test_recently_read_books_authorized(self, lclient: SankakuClient):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_recently_read_books(1).__anext__(),
            mdl.PageBook
        )

    @pytest.mark.parametrize(["post_id"], [(27038477,)])
    async def test_get_related_books(self, lclient: SankakuClient, post_id):  # noqa: D102, E501
        assert isinstance(
            await lclient.get_related_books(1, post_id=post_id).__anext__(),
            mdl.PageBook
        )

    @pytest.mark.parametrize(["book_id"], [(1000,)])
    async def test_get_book(self, nlclient: SankakuClient, book_id):  # noqa: D102
        book = await nlclient.get_book(book_id)
        assert isinstance(book, mdl.Book)

    async def test_get_non_existent_book(self, lclient: SankakuClient):  # noqa: D102
        with pytest.raises(errors.PageNotFoundError):
            await lclient.get_book(-10_000)


class TestUserClient:
    async def test_browse_users(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""

        assert isinstance(await nlclient.browse_users(1).__anext__(), mdl.User)
        assert isinstance(
            await nlclient.browse_users(1, level=types.UserLevel.MEMBER).__anext__(),
            mdl.User
        )

    @pytest.mark.parametrize(["name_or_id"], [("anonymous",), (1423490,)])
    async def test_get_user(self, nlclient: SankakuClient, name_or_id):  # noqa: D102
        assert isinstance(await nlclient.get_user(name_or_id), mdl.User)

    @pytest.mark.parametrize(["name_or_id"], [("!@#sdcvjkj|",), (-1000,)])
    async def test_get_user_with_wrong_name_or_id(  # noqa: D102
        self,
        nlclient: SankakuClient,
        name_or_id
    ):
        with pytest.raises(errors.PageNotFoundError):
            await nlclient.get_user(name_or_id)
