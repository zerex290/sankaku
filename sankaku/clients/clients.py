import json
from typing import Optional, Literal, Annotated
from collections.abc import AsyncIterator
from datetime import datetime

from loguru import logger

from .abc import ABCClient
from .http_client import HttpClient
from sankaku.typedefs import ValueRange
from sankaku.utils import from_locals
from sankaku import models as mdl, constants as const, types, errors
from sankaku.paginators import *


__all__ = [
    "PostClient",
    "AIClient",
    "TagClient",
    "BookClient",
    "UserClient",
]


class BaseClient(ABCClient):
    """Base client for login."""

    def __init__(self) -> None:
        self._profile: Optional[mdl.ExtendedUser] = None
        self._http_client: HttpClient = HttpClient()
        self._access_token: Optional[str] = None  # TODO: ability to update access token
        self._token_type: Optional[str] = None

    async def _login_via_credentials(self, login: str, password: str) -> None:
        response = await self._http_client.post(
            const.LOGIN_URL,
            data=json.dumps({"login": login, "password": password})
        )

        if not response.ok:
            raise errors.AuthorizationError(response.status, **response.json)

        self._access_token = response.json["access_token"]
        self._token_type = response.json["token_type"]
        self._profile = mdl.ExtendedUser(**response.json["current_user"])

    async def _login_via_access_token(self, access_token: str) -> None:
        try:
            self._profile = await self._get_profile(access_token)
            # Update access token and token type after successful profile fetch
            self._access_token = access_token
            self._token_type = const.DEFAULT_TOKEN_TYPE
        except errors.SankakuServerError as e:
            raise errors.AuthorizationError(e.status, **e.kwargs)

    async def _get_profile(self, access_token: str) -> mdl.ExtendedUser:
        """Get user profile information from Sankaku server by access token."""

        if self._profile is not None:
            return self._profile

        headers = {"authorization": f"{const.DEFAULT_TOKEN_TYPE} {access_token}"}
        headers.update(self._http_client.headers)
        response = await self._http_client.get(f"{const.USER_URL}/me", headers=headers)

        if not response.ok:
            raise errors.SankakuServerError(
                response.status, "Failed to get user profile", **response.json
            )

        return mdl.ExtendedUser(**response.json["user"])

    async def login(  # TODO: add two-factor auth support
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """
        Login into sankakucomplex.com via access token or credentials.
        In case when all arguments are specified, preference will be given
        to authorization by credentials.

        :param access_token: User access token
        :param login: User email or nickname
        :param password: User password
        """
        match (access_token, login, password):
            case [str(), str(), str()] | [_, str(), str()]:
                await self._login_via_credentials(login, password)  # type: ignore[arg-type]
            case [str(), _, _]:
                await self._login_via_access_token(access_token)  # type: ignore[arg-type]
            case _:
                raise errors.SankakuError(
                    "The given data is not enough "
                    "or invalid (perhaps of the wrong type)."
                )

        self._http_client.headers.update(
            authorization=f"{self._token_type} {self._access_token}"
        )
        logger.info(f"Successfully logged in as {self._profile.name}.")  # type: ignore[union-attr]

    @property
    def profile(self) -> Optional[mdl.ExtendedUser]:
        return self._profile


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
        async for page in PostPaginator(
            self._http_client, const.POST_URL, **from_locals(locals())
        ):
            for post in page.items:
                yield post

    async def get_favorited_posts(self) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get favorited posts of currently logged-in user."""

        if self._profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(favorited_by=self._profile.name):
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

        if self._profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(recommended_for=self._profile.name):
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
        async for page in Paginator(
            self._http_client,
            const.COMMENT_URL.format(post_id=post_id),
            mdl.Comment
        ):
            for comment in page.items:
                yield comment

    async def get_post(  # TODO: add related pools info if they are present
        self,
        post_id: int,
        *,
        with_similar_posts: bool = False,
        with_comments: bool = False
    ) -> mdl.Post:
        """
        Get specific post by its ID.

        :param post_id: ID of specific post
        :param with_similar_posts:  Whether to search similar posts;
        note that it greatly reduces performance
        :param with_comments: Whether to attach post comments
        """
        response = await self._http_client.get(f"{const.POST_URL}/{post_id}")

        if not response.ok:
            raise errors.PageNotFoundError(response.status, post_id=post_id)

        post = mdl.Post(**response.json)

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
        async for page in Paginator(
            self._http_client, const.AI_POST_URL,
            mdl.AIPost, **from_locals(locals())
        ):
            for post in page.items:
                yield post

    async def get_ai_post(self, post_id: int) -> mdl.AIPost:
        """
        Get specific AI post by its ID.

        :param post_id: ID of specific post
        """
        response = await self._http_client.get(f"{const.AI_POST_URL}/{post_id}")

        if not response.ok:
            raise errors.PageNotFoundError(response.status, post_id=post_id)

        return mdl.AIPost(**response.json)

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
        async for page in TagPaginator(
            self._http_client, const.TAG_URL, **from_locals(locals())
        ):
            for tag in page.items:
                yield tag

    async def get_tag(self, name_or_id: str | int) -> mdl.WikiTag:
        """
        Get specific tag by its name or ID.

        :param name_or_id: tag name or ID
        """
        ref = "name" if isinstance(name_or_id, str) else "id"
        url = const.TAG_WIKI_URL.format(ref=ref, name_or_id=name_or_id)

        response = await self._http_client.get(url)

        if not response.ok:
            raise errors.PageNotFoundError(response.status, name_or_id=name_or_id)

        return mdl.WikiTag(wiki=response.json["wiki"], **response.json["tag"])


class BookClient(BaseClient):
    """Client for book (pool) browsing."""

    async def browse_books(
        self,
        order: Optional[types.BookOrder] = None,
        rating: Optional[types.Rating] = None,
        recommended_for: Optional[str] = None,
        favorited_by: Optional[str] = None,
        tags: Optional[list[str]] = None,
        added_by: Optional[list[str]] = None,
        voted: Optional[str] = None,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None
    ) -> AsyncIterator[mdl.PageBook]:
        async for page in BookPaginator(
            self._http_client, const.BOOK_URL, **from_locals(locals())
        ):
            for book in page.items:
                yield book

    async def get_favorited_books(self) -> AsyncIterator[mdl.PageBook]:
        """Shorthand way to get favorited books for the currently logged-in user."""

        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(favorited_by=self._profile.name):
            yield book

    async def get_recommended_books(self) -> AsyncIterator[mdl.PageBook]:
        """Shorthand way to get recommended books for the currently logged-in user."""

        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(recommended_for=self._profile.name):
            yield book

    async def get_recently_read_books(self) -> AsyncIterator[mdl.PageBook]:
        """Get recently read/opened books of the currently logged-in user."""

        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(tags=[f"read:@{self._profile.id}@"]):
            yield book

    async def get_book(self, book_id: int) -> mdl.Book:
        """
        Get specific book by its ID.

        :param book_id: ID of specific book
        """
        response = await self._http_client.get(f"{const.BOOK_URL}/{book_id}")

        if not response.ok:
            raise errors.PageNotFoundError(response.status, book_id=book_id)

        return mdl.Book(**response.json)


class UserClient(BaseClient):
    """Client for browsing users."""

    async def browse_users(
        self,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None,
        *,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None
    ) -> AsyncIterator[mdl.User]:
        """
        Iterate through user pages.

        :param order: User order rule
        :param level: User level type
        :param page_number: Initial page number
        :param limit: Maximum amount of users per page
        :return: Asynchronous generator which yields users
        """
        async for page in UserPaginator(
            self._http_client, const.USER_URL, **from_locals(locals())
        ):
            for user in page.items:
                yield user

    async def get_user(self, name_or_id: str | int) -> mdl.User:
        """
        Get specific user by its name or ID.

        :param name_or_id: username or ID
        """
        url = (
            f"{const.USER_URL}/"
            f"{'name/' if isinstance(name_or_id, str) else ''}"
            f"{name_or_id}"
        )

        response = await self._http_client.get(url)

        if not response.ok:
            raise errors.PageNotFoundError(response.status, name_or_id=name_or_id)

        return mdl.User(**response.json)
