import json
from datetime import datetime
from typing import Optional, Union, List, Tuple, AsyncIterator

from typing_extensions import Literal, Annotated

from loguru import logger

from sankaku import models as mdl, constants as const, types, errors
from sankaku.paginators import *  # noqa: F403
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
    def __init__(self) -> None:
        """Base client used for login."""
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
        response = await self._http_client.get(const.PROFILE_URL, headers=headers)

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
            await self._login_via_credentials(login, password)
        elif access_token and not login and not password:
            await self._login_via_access_token(access_token)
        else:
            raise errors.SankakuError(
                "The given data is not enough "
                "or invalid (perhaps of the wrong type)."
            )

        self._http_client.headers.update(
            authorization=f"{self._token_type} {self._access_token}"
        )
        logger.info(f"Successfully logged in as {self._profile.name}.")  # type: ignore

    @property
    def profile(self) -> Optional[mdl.ExtendedUser]:
        return self._profile


class PostClient(BaseClient):
    """Client for post browsing."""
    async def browse_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
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
        voted: Optional[str] = None
    ) -> AsyncIterator[mdl.Post]:
        """Get get a certain range of posts with specific characteristics.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
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
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in PostPaginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
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
        ):
            for post in page.items[slices.pop()]:
                yield post

    async def get_favorited_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get a certain range of favorited posts of
        currently logged-in user.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        if self._profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(
            _start, _stop, _step,
            favorited_by=self._profile.name
        ):
            yield post

    async def get_top_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get a certain range of top posts.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        async for post in self.browse_posts(
            _start, _stop, _step,
            order=types.PostOrder.QUALITY
        ):
            yield post

    async def get_popular_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get a certain range of popular posts.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        async for post in self.browse_posts(
            _start, _stop, _step,
            order=types.PostOrder.POPULARITY
        ):
            yield post

    async def get_recommended_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.Post]:
        """Shorthand way to get a certain range of recommended posts for
        currently logged-in user.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        if self._profile is None:
            raise errors.LoginRequirementError

        async for post in self.browse_posts(
            _start, _stop, _step,
            recommended_for=self._profile.name
        ):
            yield post

    async def get_similar_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        post_id: int
    ) -> AsyncIterator[mdl.Post]:
        """Get a certain range of posts similar (recommended) for specific post.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            post_id: ID of the post of interest
        """
        async for post in self.browse_posts(
            _start, _stop, _step,
            tags=[f"recommended_for_post:{post_id}"]
        ):
            yield post

    async def get_post_comments(self, post_id: int) -> AsyncIterator[mdl.Comment]:
        """Get all comments of the specific post by its ID."""
        async for page in Paginator(  # noqa: F405
            const.LAST_RANGE_ITEM,
            http_client=self._http_client,
            url=const.COMMENTS_URL.format(post_id=post_id),
            model=mdl.Comment
        ):
            for comment in page.items:
                yield comment

    async def get_post(self, post_id: int) -> mdl.Post:
        """Get specific post by its ID."""
        response = await self._http_client.get(const.POST_URL.format(post_id=post_id))

        if not response.ok:
            raise errors.PageNotFoundError(response.status, post_id=post_id)

        return mdl.Post(**response.json)

    async def create_post(self):  # TODO: TBA  # noqa: D102
        raise NotImplementedError


class AIClient(BaseClient):
    """Client for working with Sankaku built-in AI."""
    async def browse_ai_posts(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.AIPost]:
        """Get a certain range of AI created posts from AI dedicated post pages.
        Range of posts can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in Paginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
            url=const.AI_POSTS_URL,
            model=mdl.AIPost
        ):
            for post in page.items[slices.pop()]:
                yield post

    async def get_ai_post(self, post_id: int) -> mdl.AIPost:
        """Get specific AI post by its ID."""
        response = await self._http_client.get(
            const.AI_POST_URL.format(post_id=post_id)
        )

        if not response.ok:
            raise errors.PageNotFoundError(response.status, post_id=post_id)

        return mdl.AIPost(**response.json)

    async def create_ai_post(self):  # TODO: TBA  # noqa: D102
        raise NotImplementedError


class TagClient(BaseClient):
    """Client for tag browsing."""
    async def browse_tags(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        tag_type: Optional[types.TagType] = None,
        order: Optional[types.TagOrder] = None,
        rating: Optional[types.Rating] = None,
        max_post_count: Optional[int] = None,
        sort_parameter: Optional[types.SortParameter] = None,
        sort_direction: Optional[types.SortDirection] = None
    ) -> AsyncIterator[mdl.PageTag]:
        """Get a certain range of tags from tag pages.
        Range of tags can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            tag_type: Tag type filter
            order: Tag order rule
            rating: Tag rating
            max_post_count: Upper threshold for number of posts with tags found
            sort_parameter: Tag sorting parameter
            sort_direction: Tag sorting direction
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in TagPaginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
            tag_type=tag_type,
            order=order,
            rating=rating,
            max_post_count=max_post_count,
            sort_parameter=sort_parameter,
            sort_direction=sort_direction
        ):
            for tag in page.items[slices.pop()]:
                yield tag

    async def get_tag(self, name_or_id: Union[str, int]) -> mdl.WikiTag:
        """Get specific tag by its name or ID."""
        response = await self._http_client.get(
            const.TAG_WIKI_URL.format(
                ref="/name" if isinstance(name_or_id, str) else "/id",
                name_or_id=name_or_id
            )
        )

        if not response.ok:
            raise errors.PageNotFoundError(response.status, name_or_id=name_or_id)

        return mdl.WikiTag(wiki=response.json["wiki"], **response.json["tag"])


class BookClient(BaseClient):
    """Client for book (pool) browsing."""
    async def browse_books(
            self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        order: Optional[types.BookOrder] = None,
        rating: Optional[types.Rating] = None,
        recommended_for: Optional[str] = None,
        favorited_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        added_by: Optional[List[str]] = None,
        voted: Optional[str] = None,
    ) -> AsyncIterator[mdl.PageBook]:
        """Get a certain range of books (pools) from book (pool) pages.
        Range of books can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            order: Book order rule
            rating: Books rating
            recommended_for: Books recommended for specified user
            favorited_by: Books favorited by specified user
            tags: Tags available for search
            added_by: Books uploaded by specified users
            voted: Books voted by specified user
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in BookPaginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
            order=order,
            rating=rating,
            recommended_for=recommended_for,
            favorited_by=favorited_by,
            tags=tags,
            added_by=added_by,
            voted=voted
        ):
            for book in page.items[slices.pop()]:
                yield book

    async def get_favorited_books(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.PageBook]:
        """Shorthand way to get a certain range of favorited books for
        currently logged-in user.
        Range of books can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(
            _start, _stop, _step,
            favorited_by=self._profile.name
        ):
            yield book

    async def get_recommended_books(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.PageBook]:
        """Shorthand way to get a certain range of recommended books for
        currently logged-in user.
        Range of books can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(
            _start, _stop, _step,
            recommended_for=self._profile.name
        ):
            yield book

    async def get_recently_read_books(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /
    ) -> AsyncIterator[mdl.PageBook]:
        """Get a certain range of recently read/opened books of currently
        logged-in user.
        Range of books can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
        """
        if self._profile is None:
            raise errors.LoginRequirementError

        async for book in self.browse_books(
            _start, _stop, _step,
            tags=[f"read:@{self._profile.id}@"]
        ):
            yield book

    async def get_related_books(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        post_id: int
    ) -> AsyncIterator[mdl.PageBook]:
        """Get a certain range of books related to specific post.
        Range of books can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            post_id: ID of the post of interest
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in BookPaginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
            url=const.RELATED_BOOKS_URL.format(post_id=post_id)
        ):
            for book in page.items[slices.pop()]:
                yield book

    async def get_book(self, book_id: int) -> mdl.Book:
        """Get specific book by its ID."""
        response = await self._http_client.get(const.BOOK_URL.format(book_id=book_id))

        if not response.ok:
            raise errors.PageNotFoundError(response.status, book_id=book_id)

        return mdl.Book(**response.json)


class UserClient(BaseClient):
    """Client for browsing users."""
    async def browse_users(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None,
    ) -> AsyncIterator[mdl.User]:
        """Get a certain range of user profiles from user pages.
        Range of user profiles can be specified in the same way as when using
        built-in `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            order: User order rule
            level: User level type
        """
        item_range = _process_item_range(_start, _stop, _step)
        page_range = _process_page_range(*item_range[:2], limit=const.BASE_LIMIT)
        slices = _compute_slices(item_range, page_range)

        async for page in UserPaginator(  # noqa: F405
            *page_range,
            http_client=self._http_client,
            order=order,
            level=level
        ):
            for user in page.items[slices.pop()]:
                yield user

    async def get_user(self, name_or_id: Union[str, int]) -> mdl.User:
        """Get specific user by its name or ID."""
        response = await self._http_client.get(
            const.USER_URL.format(
                ref="/name" if isinstance(name_or_id, str) else "",
                name_or_id=name_or_id
            )
        )

        if not response.ok:
            raise errors.PageNotFoundError(response.status, name_or_id=name_or_id)

        return mdl.User(**response.json)


def _process_item_range(
    _start: int,
    _stop: Optional[int] = None,
    _step: Optional[int] = None
) -> Tuple[int, int, int]:
    if _stop is None and _step is None:
        _item_start = const.BASE_RANGE_START
        _item_stop = _start
        _item_step = const.BASE_RANGE_STEP
    elif _stop is not None and _step is None:
        _item_start = _start
        _item_stop = _stop
        _item_step = const.BASE_RANGE_STEP
    else:
        _item_start = _start
        _item_stop = _stop
        _item_step = _step
    return _item_start, _item_stop, _item_step  # type: ignore


def _process_page_range(
    _item_start: int,
    _item_stop: int,
    *,
    limit: Annotated[int, ValueRange(1, 100)]
) -> Tuple[int, int, int]:
    _page_start = _item_start // limit
    _page_stop = _item_stop // limit + (1 if _item_stop % limit else 0)
    _page_step = const.BASE_RANGE_STEP
    return _page_start, _page_stop, _page_step


def _compute_slices(
    _item_range: Tuple[int, int, int],
    _page_range: Tuple[int, int, int]
) -> List[slice]:
    """Compute slices for further subscription of page items.

    Usage:
        ```
        slices = _compute_slices(_item_range, _page_range)
        for page in Paginator(...):
            for item in page.items(slices.pop()):
                ...
        ```
    """
    # Flat view of item indexes
    items = range(*_item_range)
    pages = range(*_page_range)
    # Reshaped view with grouping item indexes inside relevant page lists.
    reshaped = [[] for _ in pages]
    for i in items:
        page_number = i // const.BASE_LIMIT
        reshaped[pages.index(page_number)].append(i - page_number*const.BASE_LIMIT)

    slices: List[slice] = []
    template = range(const.BASE_LIMIT)
    for page in reshaped:
        slices.append(
            slice(
                template.index(page[0]),
                template.index(page[-1]) + 1,
                _item_range[-1]
            )
        )

    # Reverse slices objects for for further usage of slices.pop() with
    # default behaviour. Without reversing slices list it must be popped from
    # head (slices.pop(0)), which will cause internal array shifting and memory
    # reallocations at every iteration.
    return list(reversed(slices))
