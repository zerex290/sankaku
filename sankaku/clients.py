import json
from typing import Optional, Literal, Annotated, Any
from collections.abc import AsyncIterator
from datetime import datetime

import aiohttp
from loguru import logger

import sankaku.models as mdl
from sankaku.typedefs import ValueRange
from sankaku import constants as const, types, errors
from sankaku.paginators import *


class BaseClient:
    """Base client for login."""

    def __init__(self) -> None:
        self.profile: Optional[mdl.ExtendedUser] = None
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._token_type: str = ""
        self._auth: bool = False  # Flag that specifies API requests type

    async def login(self, login: str, password: str) -> None:
        """
        Login into sankakucomplex.com via login and password.

        :param login: User email or username
        :param password: User password
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                const.LOGIN_URL,
                headers=self._headers,
                data=json.dumps({"login": login, "password": password})
            ) as response:
                logger.debug(f"Sent POST request [{response.status}]: {response.url}")
                data = await response.json()

                if not response.ok:
                    raise errors.AuthorizationError(response.status, data.get("error"))

                self._token_type = data["token_type"]
                self._access_token = data["access_token"]
                self._refresh_token = data["refresh_token"]
                self.profile = mdl.ExtendedUser(**data["current_user"])
                self._auth = True
                logger.info(f"Successfully logged in as {self.profile.name}.")

    @property
    def _headers(self) -> dict[str, str]:
        headers = const.HEADERS.copy()
        if self._auth:
            headers["authorization"] = f"{self._token_type} {self._access_token}"
        return headers

    @property
    def _session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(headers=self._headers)

    @staticmethod
    def _get_paginator_kwargs(
        loc: dict[str, Any],
        rm_list: tuple[str, ...] = ("self", "session")
    ) -> dict[str, Any]:
        """
        Get kwargs for paginator from locals of calling function.

        :param loc: locals of outer function
        :param rm_list: positions from calling function to be removed
        """
        return {k: v for k, v in loc.copy().items() if k not in rm_list}


class PostClient(BaseClient):
    """Client for post browsing."""

    async def browse_posts(
        self,
        order: Optional[types.PostOrder] = None,
        date: Optional[list[datetime]] = None,
        rating: Optional[types.Rating] = None,
        threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]] = None,
        file_size: Optional[types.FileSize] = None,
        file_type: Optional[types.FileType] = None,
        video_duration: Optional[list[int]] = None,
        recommended_for: Optional[str] = None,
        favorited_by: Optional[str] = None,
        tags: Optional[list[str]] = None,
        added_by: Optional[list[str]] = None,
        voted: Optional[str] = None,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None

    ) -> AsyncIterator[mdl.Post]:
        """
        Iterate through the post browser.

        :param order: Post order rule
        :param date: Date or range of dates
        :param rating: Post rating
        :param threshold: Vote (quality) filter of posts
        :param hide_posts_in_books: Whether show post from books or not
        :param file_size: Size (aspect ratio) of mediafile
        :param file_type: Type of mediafile in post
        :param video_duration: Video duration in seconds or in range of seconds
        :param recommended_for: Display posts recommended for specified user
        :param favorited_by: Users added post to their favourites
        :param tags: Tags available for search
        :param added_by: Posts uploaded by specified user
        :param voted: Posts voted by specified user
        :param page_number: Initial page number
        :param limit: Maximum amount of posts per page
        :return: Asynchronous generator which yields posts
        """
        async with self._session as session:
            async for page in PostPaginator(
                session, const.POST_URL,
                **self._get_paginator_kwargs(locals())
            ):
                for post in page.data:
                    yield post

    async def get_favorited_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get favorite posts of currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(favorited_by=self.profile.name):
            yield post

    async def get_top_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get top posts."""

        async for post in self.browse_posts(order=types.PostOrder.QUALITY):
            yield post

    async def get_popular_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get popular posts."""

        async for post in self.browse_posts(order=types.PostOrder.POPULARITY):
            yield post

    async def get_recommended_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get recommended posts for the currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(recommended_for=self.profile.name):
            yield post

    async def get_similar_posts(self, post_id: int) -> AsyncIterator[mdl.Post]:
        """
        Get posts similar (recommended) for specific post.

        :param post_id: ID of specific post
        :return: Asynchronous generator which yields similar posts
        """
        tag = f"recommended_for_post:{post_id}"
        async for post in self.browse_posts(tags=[tag]):
            yield post

    async def get_post_comments(self, post_id: int) -> AsyncIterator[mdl.Comment]:
        """
        Get comments on the post.

        :param post_id: ID of specific post
        """
        async with self._session as session:
            async for page in CommentPaginator(
                session, const.COMMENT_URL.format(post_id=post_id)
            ):
                for comment in page.data:
                    yield comment

    async def get_post(
        self,
        post_id: int,
        *,
        with_similar_posts: bool = False,
        with_comments: bool = False
    ) -> mdl.ExtendedPost:
        """
        Get specific post by its ID.

        :param post_id: ID of specific post
        :param with_similar_posts:  Whether to search similar posts;
        note that it greatly reduces performance
        :param with_comments: Whether to attach post comments
        """
        async with self._session as session:
            async with session.get(
                f"{const.POST_URL}/{post_id}",
            ) as response:
                logger.debug(f"Sent POST request [{response.status}]: {response.url}")
                if not response.ok:
                    raise errors.PostNotFoundError(post_id)
                data = await response.json()
                logger.debug(f"Response JSON: {data}")
                post = mdl.ExtendedPost(**data)

        if with_similar_posts:
            post.similar_posts = [
                sim async for sim in self.get_similar_posts(post_id)
            ]
        if with_comments:
            post.comments = [
                com async for com in self.get_post_comments(post_id)
            ]
        return post

    async def create_post(self):  # TODO: TBA
        raise NotImplementedError


class AIClient(BaseClient):
    """Client for working with Sankaku built-in AI."""

    async def browse_ai_posts(
        self,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None
    ) -> AsyncIterator[mdl.AIPost]:
        """
        Iterate through the AI post browser.

        :param page_number: Initial page number
        :param limit: Maximum amount of posts per page
        :return: Asynchronous generator which yields AI posts
        """
        async with self._session as session:
            async for page in AIPostPaginator(
                session, const.AI_POST_URL,
                **self._get_paginator_kwargs(locals())
            ):
                for post in page.data:
                    yield post

    async def get_ai_post(self, post_id: int) -> mdl.AIPost:
        """
        Get specific AI post by its ID.

        :param post_id: ID of specific post
        """
        async with self._session as session:
            async with session.get(f"{const.AI_POST_URL}/{post_id}") as response:
                logger.debug(f"Sent POST request [{response.status}]: {response.url}")
                if not response.ok:
                    raise errors.PostNotFoundError(post_id)
                data = await response.json()
                logger.debug(f"Response JSON: {data}")
                return mdl.AIPost(**data)

    async def create_ai_post(self):  # TODO: TBA
        raise NotImplementedError


class TagClient(BaseClient):
    """Client for tag browsing."""

    async def browse_tags(
        self,
        tag_type: Optional[types.TagType] = None,  # TODO: ability to specify multiple tags
        order: Optional[types.TagOrder] = None,
        rating: Optional[types.Rating] = None,
        max_post_count: Optional[int] = None,
        sort_parameter: Optional[types.SortParameter] = None,
        sort_direction: Optional[types.SortDirection] = None,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None

    ) -> AsyncIterator[mdl.PageTag]:
        """
        Iterate through the tag pages.

        :param tag_type: Tag type filter
        :param order: Tag order rule
        :param rating: Tag rating
        :param max_post_count: Upper threshold for number of posts with tags found
        :param sort_parameter: Tag sorting parameter
        :param sort_direction: Tag sorting direction
        :param page_number: Initial page number
        :param limit: Maximum amount of tags per page
        :return: Asynchronous generator which yields tags
        """
        async with self._session as session:
            async for page in TagPaginator(
                session, const.TAG_URL,
                **self._get_paginator_kwargs(locals())
            ):
                for tag in page.data:
                    yield tag

    async def get_tag(self, name_or_id: str | int) -> mdl.WikiTag:
        """
        Get specific tag by its name or ID.

        :param name_or_id: tag name or ID
        :return:
        """
        ref = "name" if isinstance(name_or_id, str) else "id"
        url = const.TAG_WIKI_URL.format(ref=ref, name_or_id=name_or_id)
        async with self._session as session:
            async with session.get(url) as response:
                logger.debug(f"Sent POST request [{response.status}]: {response.url}")
                if not response.ok:
                    raise errors.TagNotFoundError(name_or_id)
                data = await response.json()
                logger.debug(f"Response JSON: {data}")
                return mdl.WikiTag(wiki=data["wiki"], **data["tag"])


class BookClient(BaseClient):
    """Client for book (pool) browsing."""

    async def browse_books(self):  # TODO: TBA
        raise NotImplementedError

    async def get_recommended_books(self):  # TODO: TBA
        """Shorthand way to get recommended books for the currently logged-in user."""

        raise NotImplementedError


class UserClient(BaseClient):
    """Client for browsing users."""

    async def browse_users(
        self,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None
    ) -> AsyncIterator[mdl.User | mdl.ShortenedUser]:
        """
        Iterate through user pages.

        :param order: User order rule
        :param level: User level type
        :param page_number: Initial page number
        :param limit: Maximum amount of users per page
        :return: Asynchronous generator which yields users
        """
        logger.warning(f"Chance to get ShortenedUser model with fewer attributes.")
        async with self._session as session:
            async for page in UserPaginator(
                session, const.USER_URL,
                **self._get_paginator_kwargs(locals())
            ):
                for user in page.data:
                    yield user

    async def get_user(self, username: str):  # TODO: TBA
        raise NotImplementedError


class SankakuClient(  # noqa
    PostClient,
    AIClient,
    TagClient,
    BookClient,
    UserClient
):
    """Simple client for Sankaku API."""
