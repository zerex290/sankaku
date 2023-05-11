from datetime import datetime

import pytest  # noqa

from sankaku import errors, models as mdl, types
from sankaku.clients import SankakuClient


class TestBaseClient:
    async def test_login_with_invalid_data(self, nlclient: SankakuClient):
        with pytest.raises(errors.AuthorizationError):
            await nlclient.login("incorrect_login", "incorrect_password")

    async def test_login_with_valid_data(self, lclient: SankakuClient):
        assert isinstance(lclient.profile, mdl.ExtendedUser)


class TestPostClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await anext(nlclient.browse_posts()), mdl.Post)

    @pytest.mark.parametrize(
        ["file_type", "video_duration", "expected"],
        [(types.FileType.IMAGE, [1, 60], errors.VideoDurationError)]
    )
    async def test_browse_with_incompatible_args(
        self, nlclient: SankakuClient,
        file_type, video_duration, expected
    ):
        """Case when arguments are incompatible."""
        with pytest.raises(expected):
            await anext(
                nlclient.browse_posts(
                    file_type=file_type, video_duration=video_duration
                )
            )

    @pytest.mark.parametrize(["page_number", "limit"], [(-1, 40), (1, -40)])
    async def test_browse_with_incorrect_page_number_or_limit(
        self, nlclient: SankakuClient,
        page_number, limit
    ):
        posts: list[mdl.Post] = []
        async for post in nlclient.browse_posts(
            page_number=page_number, limit=limit
        ):
            posts.append(post)
        assert not posts

    @pytest.mark.parametrize(
        [
            "page_number", "limit", "hide_posts_in_books", "order",
            "date", "rating", "threshold", "file_size", "file_type",
            "video_duration", "recommended_for", "favorited_by", "tags",
            "added_by", "voted"

        ],
        [
            (
                1, 50, "always", types.PostOrder.POPULARITY,
                None, None, None, None, None,
                None, None, None, None,
                None, None
            ),
            (
                1, 40, "in-larger-tags", types.PostOrder.QUALITY,
                None, types.Rating.EXPLICIT, None, None, types.FileType.IMAGE,
                None, "Moldus", None, None,
                None, None
            ),
            (
                1, 10, None, types.PostOrder.DATE,
                [datetime(2018, 6, 16)], None, 4, None, types.FileType.VIDEO,
                [1, 900], None, None, ["animated"],
                ["anonymous"], "Nigredo"
            ),
            (
                1, 10, None, types.PostOrder.DATE,
                None, None, 4, types.FileSize.LARGE, None,
                None, None, "Moldus", ["female", "solo"],
                None, None
            )
        ]
    )
    async def test_browse_with_random_args(
        self, lclient: SankakuClient,
        page_number, limit, hide_posts_in_books, order,
        date, rating, threshold, file_size, file_type,
        video_duration, recommended_for, favorited_by, tags,
        added_by, voted
    ):
        kwargs = locals().copy()
        del kwargs["self"], kwargs["lclient"]
        post = await anext(lclient.browse_posts(**kwargs))
        assert isinstance(post, mdl.Post)

    async def test_get_favorited_posts_unauthorized(self, nlclient: SankakuClient):
        with pytest.raises(errors.LoginRequirementError):
            await anext(nlclient.get_favorited_posts())

    async def test_get_favorited_posts_authorized(self, lclient: SankakuClient):
        assert isinstance(await anext(lclient.get_favorited_posts()), mdl.Post)

    async def test_get_top_posts(self, nlclient: SankakuClient):
        assert isinstance(await anext(nlclient.get_top_posts()), mdl.Post)

    async def test_get_popular_posts(self, nlclient: SankakuClient):
        assert isinstance(await anext(nlclient.get_popular_posts()), mdl.Post)

    async def test_get_recommended_posts_unauthorized(self, nlclient: SankakuClient):
        with pytest.raises(errors.LoginRequirementError):
            await anext(nlclient.get_recommended_posts())

    async def test_get_recommended_posts_authorized(self, lclient: SankakuClient):
        assert isinstance(await anext(lclient.get_recommended_posts()), mdl.Post)

    @pytest.mark.parametrize(
        ["post_id", "with_similar_posts", "with_comments"],
        [
            (32948875, False, False),
            (32948875, True, False),
            (33108291, False, True)
        ]
    )
    async def test_get_post(
        self, nlclient: SankakuClient,
        post_id, with_similar_posts, with_comments
    ):
        post = await nlclient.get_post(
            post_id,
            with_similar_posts=with_similar_posts,
            with_comments=with_comments
        )
        assert isinstance(post, mdl.ExtendedPost)
        if with_similar_posts:
            assert post.similar_posts
        if with_comments:
            assert post.comments

    async def test_get_non_existent_post(self, lclient: SankakuClient):
        with pytest.raises(errors.PostNotFoundError):
            await lclient.get_post(-10_000)

    async def test_create_post(self, lclient: SankakuClient):
        with pytest.raises(NotImplementedError):
            await lclient.create_post()


class TestAIClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await anext(nlclient.browse_ai_posts()), mdl.AIPost)

    @pytest.mark.parametrize(["page_number", "limit"], [(-1, 50), (1, -50)])
    async def test_browse_with_incorrect_page_number_or_limit(
        self, nlclient: SankakuClient,
        page_number, limit
    ):
        posts: list[mdl.AIPost] = []
        async for post in nlclient.browse_ai_posts(
            page_number=page_number, limit=limit
        ):
            posts.append(post)
        assert not posts

    @pytest.mark.parametrize(["post_id"], [(123,), (1721,)])
    async def test_get_ai_post(self, nlclient: SankakuClient, post_id):
        post = await nlclient.get_ai_post(post_id,)
        assert isinstance(post, mdl.AIPost)

    async def test_get_non_existent_ai_post(self, lclient: SankakuClient):
        with pytest.raises(errors.PostNotFoundError):
            await lclient.get_ai_post(-10_000)

    async def test_create_ai_post(self, lclient: SankakuClient):
        with pytest.raises(NotImplementedError):
            await lclient.create_ai_post()


class TestTagClient:
    async def test_browse_default(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(await anext(nlclient.browse_tags()), mdl.PageTag)

    @pytest.mark.parametrize(["page_number", "limit"], [(-1, 22), (1, -86)])
    async def test_browse_with_incorrect_page_number_or_limit(
        self, nlclient: SankakuClient,
        page_number, limit
    ):
        tags: list[mdl.PageTag] = []
        async for tag in nlclient.browse_tags(page_number=page_number, limit=limit):
            tags.append(tag)
        assert not tags

    @pytest.mark.parametrize(
        [
            "page_number", "limit", "tag_type",
            "order", "rating", "max_post_count",
            "sort_parameter", "sort_direction"
        ],
        [
            (
                7, 20, types.TagType.CHARACTER,
                None, types.Rating.SAFE, None,
                None, types.SortDirection.DESC
            ),
            (
                8, 60, types.TagType.COPYRIGHT,
                types.TagOrder.POPULARITY, types.Rating.QUESTIONABLE, None,
                None, types.SortDirection.ASC
            ),
            (
                18, 10, None,
                None, types.Rating.QUESTIONABLE, 2_537_220,
                types.SortParameter.NAME, types.SortDirection.ASC
            )
        ]
    )
    async def test_browse_with_random_args(
        self, lclient: SankakuClient,
        page_number, limit, tag_type,
        order, rating, max_post_count,
        sort_parameter, sort_direction
    ):
        kwargs = locals().copy()
        del kwargs["self"], kwargs["lclient"]
        tag = await anext(lclient.browse_tags(**kwargs))
        assert isinstance(tag, mdl.PageTag)

    @pytest.mark.parametrize(
        ["name_or_id"], [("animated",), (100,)]
    )
    async def test_get_tag(self, lclient: SankakuClient, name_or_id):
        wiki_tag = await lclient.get_tag(name_or_id)
        assert isinstance(wiki_tag, mdl.WikiTag)


class TestBookClient:
    async def test_browse_books(self, nlclient: SankakuClient):
        with pytest.raises(NotImplementedError):
            await nlclient.browse_books()

    async def test_get_recommended_books(self, nlclient: SankakuClient):
        with pytest.raises(NotImplementedError):
            await nlclient.get_recommended_books()


class TestUserClient:
    async def test_browse_users(self, nlclient: SankakuClient):
        """Default behaviour when unauthorized user don't set any arguments."""
        assert isinstance(
            await anext(nlclient.browse_users(level=types.UserLevel.MEMBER)),
            mdl.User
        )
        assert isinstance(
            await anext(nlclient.browse_users(types.UserOrder.POSTS)),
            mdl.ShortenedUser
        )

    async def test_get_user(self, nlclient: SankakuClient):
        with pytest.raises(NotImplementedError):
            await nlclient.get_user("Nigredo")
