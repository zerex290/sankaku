import json
from typing import Optional, Literal, Annotated, Any
from collections.abc import AsyncIterator
from datetime import datetime

import aiohttp

import sankaku.models as mdl
from sankaku.typedefs import ValueRange
from sankaku import constants, types, errors
from sankaku.paginators import *


class BaseClient:
    """Base client for login."""

    _HEADERS: dict[str, str] = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 "
            "Yowser/2.5 Safari/537.36"
        ),
        "content-type": "application/json; charset=utf-8",
        "x-requested-with": "com.android.browser",
        "accept-encoding": "gzip, deflate, br",
        "host": "capi-v2.sankakucomplex.com"
    }

    def __init__(self) -> None:
        self.profile: Optional[mdl.ExtendedProfile] = None
        self.access_token: str = ""
        self.refresh_token: str = ""
        self._token_type: str = ""

    async def login(self, login: str, password: str) -> None:
        """
        Login into sankakucomplex.com via login and password.

        :param login: User email or username
        :param password: User password
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.LOGIN_URL,
                headers=self._get_headers(),
                data=json.dumps({"login": login, "password": password})
            ) as response:
                data = await response.json()

                if not response.ok:
                    raise errors.AuthorizationError(response.status, data.get("error"))

                self._token_type = data["token_type"]
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]

                self.profile = mdl.ExtendedProfile(**data["current_user"])

    def _get_headers(self, *, auth: bool = False) -> dict[str, str]:
        headers = self._HEADERS.copy()
        if auth and not all(self.__dict__.values()):
            raise errors.LoginRequirementError
        elif auth:
            headers["authorization"] = f"{self._token_type} {self.access_token}"
        return headers

    @staticmethod
    def _get_paginator_kwargs(
        loc: dict[str, Any],
        rm_list: tuple[str, ...] = ("self", "auth")
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
        *,
        auth: bool = False,
        page_number: int = 1,
        limit: Annotated[int, ValueRange(1, 100)] = 40,
        hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]] = None,
        order: Optional[types.PostOrder] = None,
        date: Optional[list[datetime]] = None,
        rating: Optional[types.Rating] = None,
        threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        file_size: Optional[types.FileSize] = None,
        file_type: Optional[types.File] = None,
        video_duration: Optional[list[int]] = None,
        recommended_for: Optional[str] = None,
        favorited_by: Optional[str] = None,
        tags: Optional[list[str]] = None,
        added_by: Optional[list[str]] = None,
        voted: Optional[str] = None
    ) -> AsyncIterator[mdl.Post]:
        """
        Iterate through the post browser.

        :param auth: Whether to make request on behalf of currently logged-in user
        :param page_number: Current page number
        :param limit: Maximum amount of posts per page
        :param hide_posts_in_books: Whether show post from books or not
        :param order: Post order rule
        :param date: Date or range of dates
        :param rating: Post rating
        :param threshold: Vote (quality) filter of posts
        :param file_size: Size (aspect ratio) of mediafile
        :param file_type: Type of mediafile in post
        :param video_duration: Video duration in seconds or in range of seconds
        :param recommended_for: Display posts recommended for specified user
        :param favorited_by: Users added post to their favourites
        :param tags: Tags available for search
        :param added_by: Posts uploaded by specified user
        :param voted: Posts voted by specified user
        :return: Asynchronous generator which yields posts
        """
        async for page in PostPaginator(
            aiohttp.ClientSession(headers=self._get_headers(auth=auth)),
            url=constants.POST_BROWSE_URL,
            **self._get_paginator_kwargs(locals())
        ):
            for post in page.data:
                yield post

    async def get_favorited_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get favorite posts of currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError
        async for post in self.browse_posts(auth=True, favorited_by=self.profile.name):
            yield post

    async def get_top_posts(self, *, auth: bool = False) -> AsyncIterator[mdl.Post]:
        """
        Shorthand way to get top posts.

        :param auth: Whether to make request on behalf of currently logged-in user
        """
        async for post in self.browse_posts(auth=auth, order=types.PostOrder.QUALITY):
            yield post

    async def get_popular_posts(self, *, auth: bool = False) -> AsyncIterator[mdl.Post]:
        """
        Shorthand way to get popular posts.

        :param auth: Whether to make request on behalf of currently logged-in user
        """
        async for post in self.browse_posts(auth=auth, order=types.PostOrder.POPULARITY):
            yield post

    async def get_recommended_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get recommended posts for the currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError
        async for post in self.browse_posts(auth=True, recommended_for=self.profile.name):
            yield post

    async def get_similar_posts(
        self, post_id: int, *, auth: bool = False
    ) -> AsyncIterator[mdl.Post]:
        """
        Get posts similar (recommended) for specific post.

        :param post_id: ID of specific post
        :param auth: Whether to make request on behalf of currently logged-in user
        :return: Asynchronous generator which yields similar posts
        """
        tag = f"recommended_for_post:{post_id}"
        async for post in self.browse_posts(auth=auth, tags=[tag]):
            yield post

    async def get_post_comments(
        self, post_id: int, *, auth: bool = False,
    ) -> AsyncIterator[mdl.Comment]:
        """
        Get comments on the post.

        :param post_id: ID of specific post
        :param auth: Whether to make request on behalf of currently logged-in user
        """
        async for page in CommentPaginator(
            aiohttp.ClientSession(headers=self._get_headers(auth=auth)),
            f"{constants.POST_BROWSE_URL}/{post_id}/comments",  # TODO: move endpoint somewhere
            page_number=1, limit=40
        ):
            for comment in page.data:
                yield comment

    async def get_post(
        self,
        post_id: int,
        *,
        auth: bool = False,
        with_similar_posts: bool = False,
        with_comments: bool = False
    ) -> mdl.ExtendedPost:
        """
        Get specific post by its ID.

        :param post_id: ID of specific post
        :param auth: auth: Whether to make request on behalf of
        currently logged-in user
        :param with_similar_posts:  Whether to search similar posts;
        note that it greatly reduces performance
        :param with_comments: Whether to attach post comments
        """
        async with aiohttp.ClientSession(
            headers=self._get_headers(auth=auth)
        ) as session:
            async with session.get(
                constants.POST_BROWSE_URL,
                params={"tags": f"id_range:{post_id}"}
            ) as response:
                if not response.ok:
                    raise errors.PostNotFoundError(post_id)
                data = await response.json()
                post = mdl.ExtendedPost(**data[0])

        if with_similar_posts:
            post.similar_posts = [
                sim async for sim in self.get_similar_posts(post_id, auth=auth)
            ]
        if with_comments:
            post.comments = [
                com async for com in self.get_post_comments(post_id, auth=auth)
            ]
        return post

    async def create_post(self):  # TODO: TBA
        raise NotImplementedError


class AIClient(BaseClient):
    """Client for working with Sankaku built-in AI."""

    async def browse_ai_posts(
        self,
        *,
        auth: bool = False,
        page_number: int = 1,
        limit: Annotated[int, ValueRange(1, 100)] = 40
    ) -> AsyncIterator[mdl.AIPost]:
        """
        Iterate through the AI post browser.

        :param auth: Whether to make request on behalf of currently logged-in user
        :param page_number: Current page number
        :param limit: Maximum amount of posts per page
        :return: Asynchronous generator which yields AI posts
        """
        async for page in AIPostPaginator(
            aiohttp.ClientSession(headers=self._get_headers(auth=auth)),
            url=constants.AI_POST_BROWSE_URL,
            **self._get_paginator_kwargs(locals())
        ):
            for post in page.data:
                yield post

    async def create_ai_post(self):  # TODO: TBA
        raise NotImplementedError


class TagClient(BaseClient):
    """Client for tag browsing."""

    async def browse_tags(
        self,
        *,
        auth: bool = False,
        page_number: int = 1,
        limit: Annotated[int, ValueRange(1, 100)] = 50,
        tag_type: Optional[types.Tag] = None,  # TODO: ability to specify multiple tags
        order: Optional[types.TagOrder] = None,
        rating: Optional[types.Rating] = None,
        max_post_count: Optional[int] = None,
        sort_parameter: Optional[types.SortParameter] = None,
        sort_direction: types.SortDirection = types.SortDirection.DESC
    ) -> AsyncIterator[mdl.Tag]:
        """
        Iterate through the tag pages.

        :param auth: Whether to make request on behalf of currently logged-in user
        :param page_number: Current page number
        :param limit: Maximum amount of posts per page
        :param tag_type: Tag type filter
        :param order: Tag order rule
        :param rating: Tag rating
        :param max_post_count: Upper threshold for number of posts with tags found
        :param sort_parameter: Tag sorting parameter
        :param sort_direction: Tag sorting direction
        :return: Asynchronous generator which yields tags
        """
        async for page in TagPaginator(
            aiohttp.ClientSession(headers=self._get_headers(auth=auth)),
            url=constants.TAG_BROWSE_URL,
            **self._get_paginator_kwargs(locals())
        ):
            for tag in page.data:
                yield tag

    async def get_tag(self, name_or_id: str | int, *, auth: bool = False) -> mdl.WikiTag:
        """
        Get specific tag by its name or ID.

        :param name_or_id: tag name or ID
        :param auth: Whether to make request on behalf of currently logged-in user
        :return:
        """
        if isinstance(name_or_id, str):
            url = f"{constants.TAG_WIKI_BROWSE_URL}/name/{name_or_id}"
        else:
            url = f"{constants.TAG_WIKI_BROWSE_URL}/id/{name_or_id}"

        async with aiohttp.ClientSession(
            headers=self._get_headers(auth=auth)
        ) as session:
            async with session.get(url) as response:
                if not response.ok:
                    raise errors.TagNotFoundError(name_or_id)
                data = await response.json()
                tag = mdl.WikiTag(wiki=data["wiki"], **data["tag"])
                return tag


class BookClient(BaseClient):
    """Client for book (pool) browsing."""

    async def browse_books(self):  # TODO: TBA
        raise NotImplementedError

    async def get_recommended_books(self):  # TODO: TBA
        """Shorthand way to get recommended books for the currently logged-in user."""

        raise NotImplementedError


class UserClient(BaseClient):
    """Client for browsing users."""

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
