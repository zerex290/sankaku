from datetime import datetime
from typing import Optional, TypeVar, List, Dict, Type

from typing_extensions import Literal, Annotated

from sankaku import models as mdl, constants as const, types, errors
from sankaku.clients import HttpClient
from sankaku.utils import ratelimit
from sankaku.typedefs import ValueRange
from .abc import ABCPaginator


__all__ = [
    "Paginator",
    "PostPaginator",
    "TagPaginator",
    "BookPaginator",
    "UserPaginator"
]

_T = TypeVar("_T")


class Paginator(ABCPaginator[_T]):
    def __init__(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        http_client: HttpClient,
        url: str,
        model: Type[_T],
        limit: Annotated[int, ValueRange(1, 100)] = const.BASE_LIMIT
    ) -> None:
        """Basic paginator for iteration in a certain range.
        Range of pages can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            http_client: Provider used for paginator to fetch pages from server
            url: Target API url
            model: Type of response model to be returned inside page items
            limit: Limit of items per each fetched page
        """
        # TODO: Raise error if self._start less than or equal 0.
        if _stop is None and _step is None:
            self._start = const.BASE_RANGE_START
            self._stop = _start
            self._step = const.BASE_RANGE_STEP
        elif _stop is not None and _step is None:
            self._start = _start
            self._stop = _stop
            self._step = const.BASE_RANGE_STEP
        else:  # Case when `_stop is not None and _step is not None`.
            self._start = _start
            self._stop = _stop
            self._step = _step
        self._current_page = self._start

        self.http_client = http_client
        self.url = url
        self.model = model
        self.limit = limit

        self.params: Dict[str, str] = {}
        self.complete_params()

    @ratelimit(rps=const.BASE_RPS)
    async def next_page(self) -> mdl.Page[_T]:
        """Get paginator next page."""
        if self._current_page >= self._stop:  # type: ignore
            raise errors.PaginatorLastPage

        response = await self.http_client.get(self.url, params=self.params)
        json_ = response.json
        if "code" in json_ and json_["code"] in const.PAGE_ALLOWED_ERRORS:
            raise errors.PaginatorLastPage
        elif "code" in json_:
            raise errors.SankakuServerError(response.status, **response.json)
        elif json_ == [] or (isinstance(json_, dict) and not json_["data"]):
            raise errors.PaginatorLastPage
        elif "data" in json_:
            response.json = json_["data"]

        self._current_page += self._step  # type: ignore
        self.params["page"] = str(self._current_page + 1)
        return self._construct_page(response.json)

    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""
        self.params["lang"] = "en"
        self.params["page"] = str(self._current_page + 1)
        self.params["limit"] = str(self.limit)

    def _construct_page(self, data: List[dict]) -> mdl.Page[_T]:
        """Construct and return page model."""
        items = [self.model(**d) for d in data]
        return mdl.Page[_T](
            number=self._current_page - self._step,  # type: ignore
            items=items
        )


class PostPaginator(Paginator[mdl.Post]):
    def __init__(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        http_client: HttpClient,
        url: str = const.POSTS_URL,
        model: Type[mdl.Post] = mdl.Post,
        limit: Annotated[int, ValueRange(1, 100)] = const.BASE_LIMIT,
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
    ) -> None:
        """Paginator for iteration in a certain range of post pages.
        Range of pages can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            http_client: Provider used for paginator to fetch pages from server
            url: Target API url
            model: Type of response model to be returned inside page items
            limit: Limit of items per each fetched page
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
        self.order = order
        self.date = date
        self.rating = rating
        self.threshold = threshold
        self.hide_posts_in_books = hide_posts_in_books
        self.file_size = file_size
        self.file_type = file_type
        self.video_duration = video_duration
        self.recommended_for = recommended_for
        self.favorited_by = favorited_by
        self.tags = tags
        self.added_by = added_by
        self.voted = voted
        super().__init__(
            _start,
            _stop,
            _step,
            http_client=http_client,
            url=url,
            model=model,
            limit=limit
        )

    def complete_params(self) -> None:  # noqa: PLR0912
        """Complete params passed to paginator for further use."""
        super().complete_params()
        if self.tags is None:
            self.tags = []

        for k, v in self.__dict__.items():
            if v is None:
                continue
            elif k in {"order", "rating", "file_type"} and v is not types.FileType.IMAGE:  #noqa: E501
                self.tags.append(f"{k}:{v.value}")
            elif k in {"threshold", "recommended_for", "voted"}:
                self.tags.append(f"{k}:{v}")
            elif k == "file_size":
                self.tags.append(self.file_size.value)  # type: ignore
            elif k == "date":
                date = "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in self.date)  # type: ignore  # noqa: E501
                self.tags.append(f"date:{date}")
            elif k == "video_duration" and self.file_type is not types.FileType.VIDEO:  # noqa
                raise errors.VideoDurationError
            elif k == "video_duration":
                duration = "..".join(str(sec) for sec in self.video_duration)  # type: ignore  # noqa: E501
                self.tags.append(f"duration:{duration}")
            elif k == "favorited_by":
                self.tags.append(f"fav:{self.favorited_by}")
            elif k == "added_by":
                for user in self.added_by:  # type: ignore
                    self.tags.append(f"user:{user}")

        if self.hide_posts_in_books is not None:
            self.params["hide_posts_in_books"] = self.hide_posts_in_books
        if self.tags:
            self.params["tags"] = " ".join(self.tags)


class TagPaginator(Paginator[mdl.PageTag]):
    def __init__(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        http_client: HttpClient,
        url: str = const.TAGS_URL,
        model: Type[mdl.PageTag] = mdl.PageTag,
        limit: Annotated[int, ValueRange(1, 100)] = const.BASE_LIMIT,
        tag_type: Optional[types.TagType] = None,
        order: Optional[types.TagOrder] = None,
        rating: Optional[types.Rating] = None,
        max_post_count: Optional[int] = None,
        sort_parameter: Optional[types.SortParameter] = None,
        sort_direction: Optional[types.SortDirection] = None
    ) -> None:
        """Paginator for iteration in a certain range of tag pages.
        Range of pages can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            http_client: Provider used for paginator to fetch pages from server
            url: Target API url
            model: Type of response model to be returned inside page items
            limit: Limit of items per each fetched page
            tag_type: Tag type filter
            order: Tag order rule
            rating: Tag rating
            max_post_count: Upper threshold for number of posts with tags found
            sort_parameter: Tag sorting parameter
            sort_direction: Tag sorting direction
        """
        self.tag_type = tag_type
        self.order = order
        self.rating = rating
        self.max_post_count = max_post_count
        self.sort_parameter = sort_parameter
        self.sort_direction = sort_direction or types.SortDirection.DESC
        super().__init__(
            _start,
            _stop,
            _step,
            http_client=http_client,
            url=url,
            model=model,
            limit=limit
        )

    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""
        super().complete_params()
        if self.tag_type is not None:
            self.params["types[]"] = str(self.tag_type.value)
        if self.order is not None:
            self.params["order"] = self.order.value
        if self.rating is not None:
            self.params["rating"] = self.rating.value
        if self.max_post_count is not None:
            self.params["amount"] = str(self.max_post_count)
        if self.sort_parameter is not None:
            self.params.update(
                sortBy=self.sort_parameter.value,
                sortDirection=self.sort_direction.value
            )


class BookPaginator(Paginator[mdl.PageBook]):
    def __init__(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        http_client: HttpClient,
        url: str = const.BOOKS_URL,
        model: Type[mdl.PageBook] = mdl.PageBook,
        limit: Annotated[int, ValueRange(1, 100)] = const.BASE_LIMIT,
        order: Optional[types.BookOrder] = None,
        rating: Optional[types.Rating] = None,
        recommended_for: Optional[str] = None,
        favorited_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        added_by: Optional[List[str]] = None,
        voted: Optional[str] = None
    ) -> None:
        """Paginator for iteration in a certain range of book (pool) pages.
        Range of pages can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            http_client: Provider used for paginator to fetch pages from server
            url: Target API url
            model: Type of response model to be returned inside page items
            limit: Limit of items per each fetched page
            order: Book order rule
            rating: Books rating
            recommended_for: Books recommended for specified user
            favorited_by: Books favorited by specified user
            tags: Tags available for search
            added_by: Books uploaded by specified users
            voted: Books voted by specified user
        """
        self.order = order
        self.rating = rating
        self.recommended_for = recommended_for
        self.favorited_by = favorited_by
        self.tags = tags
        self.added_by = added_by
        self.voted = voted
        super().__init__(
            _start,
            _stop,
            _step,
            http_client=http_client,
            url=url,
            model=model,
            limit=limit
        )

    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""
        super().complete_params()
        if self.tags is None:
            self.tags = []

        for k, v in self.__dict__.items():
            if v is None:
                continue
            elif k in {"order", "rating"}:
                self.tags.append(f"{k}:{v.value}")
            elif k in {"recommended_for", "voted"}:
                self.tags.append(f"{k}:{v}")
            elif k == "favorited_by":
                self.tags.append(f"fav:{self.favorited_by}")
            elif k == "added_by":
                for user in self.added_by:  # type: ignore[union-attr]
                    self.tags.append(f"user:{user}")

        if self.tags:
            self.params["tags"] = " ".join(self.tags)


class UserPaginator(Paginator[mdl.User]):
    def __init__(
        self,
        _start: int,
        _stop: Optional[int] = None,
        _step: Optional[int] = None,
        /,
        *,
        http_client: HttpClient,
        url: str = const.USERS_URL,
        model: Type[mdl.User] = mdl.User,
        limit: Annotated[int, ValueRange(1, 100)] = const.BASE_LIMIT,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None
    ) -> None:
        """Paginator for iteration in a certain range of user profiles pages.
        Range of pages can be specified in the same way as when using built-in
        `range()`.

        Args:
            _start: Start of the sequence
            _stop: End of the sequence (except this value itself)
            _step: Step of the sequence
            http_client: Provider used for paginator to fetch pages from server
            url: Target API url
            model: Type of response model to be returned inside page items
            limit: Limit of items per each fetched page
            order: User order rule
            level: User level type
        """
        self.order = order
        self.level = level
        super().__init__(
            _start,
            _stop,
            _step,
            http_client=http_client,
            url=url,
            model=model,
            limit=limit
        )

    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""
        super().complete_params()
        if self.order is not None:
            self.params["order"] = self.order.value
        if self.level is not None:
            self.params["level"] = str(self.level.value)
