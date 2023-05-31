import json
from datetime import datetime
from typing import Optional, Union, List, AsyncIterator

try:
    from typing import Literal, Annotated
except (ModuleNotFoundError, ImportError):
    from typing_extensions import Literal, Annotated  # type: ignore[assignment]

from loguru import logger

from sankaku import models as mdl, constants as const, types, errors
from sankaku.paginators import *
from sankaku.utils import from_locals
from sankaku.typedefs import ValueRange
from .abc import ABCClient
from .http_client import HttpClient


__all__ = [
    "PostClient",
    "AIClient",
    "TagClient",
    "BookClient",
    "UserClient",
]


class BaseClient(ABCClient):
    """Base client used for login."""
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
        response = await self._http_client.get(f"{const.PROFILE_URL}", headers=headers)

        if not response.ok:
            raise errors.SankakuServerError(
                response.status, "Failed to get user profile", **response.json
            )

        return mdl.ExtendedUser(**response.json["user"])

    async def login(
            self,
            *,
            access_token: Optional[str] = None,
            login: Optional[str] = None,
            password: Optional[str] = None
    ) -> None:
        """Login into sankakucomplex.com via access token or credentials.
        In case when all arguments are specified, preference will be given
        to authorization by credentials.

        Args:
            access_token: User access token
            login: User email or nickname
            password: User password
        """
        if login and password:
            await self._login_via_credentials(login, password)  # type: ignore[arg-type]
        elif access_token and not login and not password:
            await self._login_via_access_token(access_token)  # type: ignore[arg-type]
        else:
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
            date: Optional[List[datetime]] = None,
            rating: Optional[types.Rating] = None,
            threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
            hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]] = None,
            file_size: Optional[types.FileSize] = None,
            file_type: Optional[types.FileType] = None,
            video_duration: Optional[List[int]] = None,
            recommended_for: Optional[str] = None,
            favorited_by: Optional[str] = None,
            tags: Optional[List[str]] = None,
            added_by: Optional[List[str]] = None,
            voted: Optional[str] = None,
            *,
            page_number: Optional[int] = None,
            limit: Optional[Annotated[int, ValueRange(1, 100)]] = None

    ) -> AsyncIterator[mdl.Post]:
        """Get posts from post pages.

        Args:
            order: Post order rule
            date: Date or range of dates
            rating: Post rating
            threshold: Vote (quality) filter of posts
            hide_posts_in_books: Whether show post from books or not
            file_size: Size (aspect ratio) of mediafile
            file_type: Type of mediafile in post
            video_duration: Video duration in seconds or in range of seconds
            recommended_for: Posts recommended for specified user
            favorited_by: Posts favorited by specified user
            tags: Tags available for search
            added_by: Posts uploaded by specified users
            voted: Posts voted by specified user
            page_number: Page number from which to start iteration
            limit: Maximum amount of posts per page
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
        """Get posts similar (recommended) for specific post by its ID."""
        tag = f"recommended_for_post:{post_id}"
        async for post in self.browse_posts(tags=[tag]):
            yield post

    async def get_post_comments(self, post_id: int) -> AsyncIterator[mdl.Comment]:
        """Get comments of the specific post by its ID."""
        async for page in Paginator(
                self._http_client,
                const.COMMENT_URL.format(post_id=post_id),
                mdl.Comment
        ):
            for comment in page.items:
                yield comment

    async def get_post(self, post_id: int) -> mdl.Post:
        """Get specific post by its ID."""
        response = await self._http_client.get(f"{const.POST_URL}/{post_id}")

        if not response.ok:
            raise errors.PageNotFoundError(response.status, post_id=post_id)

        return mdl.Post(**response.json)

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
        """Get AI created posts from AI dedicated post pages.

        Args:
            page_number: Page number from which to start iteration
            limit: Maximum amount of posts per page
        """
        async for page in Paginator(
                self._http_client, const.AI_POST_URL,
                mdl.AIPost, **from_locals(locals())
        ):
            for post in page.items:
                yield post

    async def get_ai_post(self, post_id: int) -> mdl.AIPost:
        """Get specific AI post by its ID."""
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
        """Get tags from tag pages.

        Args:
            tag_type: Tag type filter
            order: Tag order rule
            rating: Tag rating
            max_post_count: Upper threshold for number of posts with tags found
            sort_parameter: Tag sorting parameter
            sort_direction: Tag sorting direction
            page_number: Page number from which to start iteration
            limit: Maximum amount of tags per page
        """
        async for page in TagPaginator(
                self._http_client, const.TAG_URL, **from_locals(locals())
        ):
            for tag in page.items:
                yield tag

    async def get_tag(self, name_or_id: Union[str, int]) -> mdl.WikiTag:
        """Get specific tag by its name or ID."""
        ref = "/name" if isinstance(name_or_id, str) else "/id"
        url = f"{const.TAG_WIKI_URL}{ref}/{name_or_id}"

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
            tags: Optional[List[str]] = None,
            added_by: Optional[List[str]] = None,
            voted: Optional[str] = None,
            *,
            page_number: Optional[int] = None,
            limit: Optional[Annotated[int, ValueRange(1, 100)]] = None
    ) -> AsyncIterator[mdl.PageBook]:
        """Get books from book (pool) pages.

        Args:
            order: Book order rule
            rating: Books rating
            recommended_for: Books recommended for specified user
            favorited_by: Books favorited by specified user
            tags: Tags available for search
            added_by: Books uploaded by specified users
            voted: Books voted by specified user
            page_number: Page number from which to start iteration
            limit: Maximum amount of books per page
        """
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

    async def get_related_books(self, post_id: int) -> AsyncIterator[mdl.PageBook]:
        """Get books related to specific post by its ID."""
        async for page in BookPaginator(
                self._http_client, const.RELATED_BOOK_URL.format(post_id=post_id)
        ):
            for book in page.items:
                yield book

    async def get_book(self, book_id: int) -> mdl.Book:
        """Get specific book by its ID."""
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
        """Get user profiles from user pages.

        Args:
            order: User order rule
            level: User level type
            page_number: Page number from which to start iteration
            limit: Maximum amount of users per page
        """
        async for page in UserPaginator(
                self._http_client, const.USER_URL, **from_locals(locals())
        ):
            for user in page.items:
                yield user

    async def get_user(self, name_or_id: Union[str, int]) -> mdl.User:
        """Get specific user by its name or ID."""
        ref = "/name" if isinstance(name_or_id, str) else ""
        url = f"{const.USER_URL}{ref}/{name_or_id}"

        response = await self._http_client.get(url)

        if not response.ok:
            raise errors.PageNotFoundError(response.status, name_or_id=name_or_id)

        return mdl.User(**response.json)
