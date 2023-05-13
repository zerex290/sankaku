from typing import Optional, Literal, Annotated, TypeVar
from datetime import datetime

from .abc import ABCPaginator
from sankaku.typedefs import ValueRange
from sankaku.utils import ratelimit
from sankaku import models as mdl, constants as const, types, errors
from sankaku.clients import HttpClient


__all__ = [
    "Paginator",
    "PostPaginator",
    "TagPaginator",
    "UserPaginator"
]


_T = TypeVar("_T")


class Paginator(ABCPaginator[_T]):
    """Basic paginator for iteration without any special parameters."""

    def __init__(
        self,
        http_client: HttpClient,
        url: str,
        model: type[_T],
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None
    ) -> None:
        self.http_client = http_client
        self.url = url
        self.model = model
        self.page_number = page_number or const.BASE_PAGE_NUMBER
        self.limit = limit or const.BASE_PAGE_LIMIT
        self.params: dict[str, str] = params or {}

        self.complete_params()

    @ratelimit(rps=const.BASE_RPS)
    async def next_page(self) -> mdl.Page[_T]:  # type: ignore[override]
        response = await self.http_client.get(self.url, params=self.params)
        match response.json:
            case [] | {"data": []}:
                raise errors.PaginatorLastPage(response.status, page=self.page_number)
            case {"code": code} if code in const.PAGE_ALLOWED_ERRORS:
                raise errors.PaginatorLastPage(response.status, page=self.page_number)
            case {"code": _, "errorId": _}:
                raise errors.SankakuServerError(response.status, **response.json)
            case {"data": list() as data} if data:
                response.json = data

        self.page_number += 1
        self.params["page"] = str(self.page_number)
        return self.construct_page(response.json)

    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""

        self.params["lang"] = "en"
        if self.page_number is not None:
            self.params["page"] = str(self.page_number)
        if self.limit is not None:
            self.params["limit"] = str(self.limit)

    def construct_page(self, data: list[dict]) -> mdl.Page[_T]:
        """Construct and return page model."""

        items = [self.model(**d) for d in data]
        return mdl.Page[_T](number=self.page_number - 1, items=items)


class PostPaginator(Paginator[mdl.Post]):

    def __init__(
        self,
        http_client: HttpClient,
        url: str,
        model: type[mdl.Post] = mdl.Post,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None,
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
        voted: Optional[str] = None
    ) -> None:
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
        super().__init__(http_client, url, model, page_number, limit, params)

    def complete_params(self) -> None:
        super().complete_params()
        if self.tags is None:
            self.tags = []

        for items in self.__dict__.items():
            match items:
                case [_, None]:
                    continue
                case ["rating" | "order" | "file_type" as k, v] if v != types.FileType.IMAGE:  # noqa
                    self.tags.append(f"{k}:{v.value}")
                case ["threshold" | "recommended_for" | "voted" as k, v]:
                    self.tags.append(f"{k}:{v}")
                case ["file_size", _]:
                    self.tags.append(self.file_size.value)  # type: ignore[union-attr]
                case ["date", _]:
                    date = "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in self.date)  # type: ignore[union-attr]
                    self.tags.append(f"date:{date}")
                case ["video_duration", _] if self.file_type != types.FileType.VIDEO:  # noqa
                    raise errors.VideoDurationError
                case ["video_duration", _]:
                    duration = "..".join(str(sec) for sec in self.video_duration)  # type: ignore[union-attr]
                    self.tags.append(f"duration:{duration}")
                case ["favorited_by", _]:
                    self.tags.append(f"fav:{self.favorited_by}")
                case ["added_by", _]:
                    for user in self.added_by:  # type: ignore[union-attr]
                        self.tags.append(f"user:{user}")

        if self.hide_posts_in_books is not None:
            self.params["hide_posts_in_books"] = self.hide_posts_in_books
        if self.tags:
            self.params["tags"] = " ".join(self.tags)


class TagPaginator(Paginator[mdl.PageTag]):
    def __init__(
        self,
        http_client: HttpClient,
        url: str,
        model: type[mdl.PageTag] = mdl.PageTag,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None,
        tag_type: Optional[types.TagType] = None,
        order: Optional[types.TagOrder] = None,
        rating: Optional[types.Rating] = None,
        max_post_count: Optional[int] = None,
        sort_parameter: Optional[types.SortParameter] = None,
        sort_direction: Optional[types.SortDirection] = None
    ) -> None:
        self.tag_type = tag_type
        self.order = order
        self.rating = rating
        self.max_post_count = max_post_count
        self.sort_parameter = sort_parameter
        self.sort_direction = sort_direction or types.SortDirection.DESC
        super().__init__(http_client, url, model, page_number, limit, params)

    def complete_params(self) -> None:
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


class UserPaginator(Paginator[mdl.User]):
    def __init__(
        self,
        http_client: HttpClient,
        url: str,
        model: type[mdl.User] = mdl.User,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None
    ) -> None:
        self.order = order
        self.level = level
        super().__init__(http_client, url, model, page_number, limit, params)

    def complete_params(self) -> None:
        super().complete_params()
        if self.order is not None:
            self.params["order"] = self.order.value
        if self.level is not None:
            self.params["level"] = str(self.level.value)
