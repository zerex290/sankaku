from abc import ABC, abstractmethod
from typing import Optional, Literal, Annotated, Any
from collections.abc import AsyncIterator, Sequence, Mapping
from datetime import datetime

import aiohttp
from loguru import logger

import sankaku.models as mdl
from sankaku.typedefs import ValueRange
from sankaku import constants as const, types, utils, errors


__all__ = [
    "CommentPaginator",
    "PostPaginator",
    "AIPostPaginator",
    "TagPaginator",
    "UserPaginator"
]


class BasePaginator(ABC):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None
    ) -> None:
        self.session = session
        self.url = url
        self.page_number = page_number or const.BASE_PAGE_NUMBER
        self.limit = limit or const.BASE_PAGE_LIMIT
        self.params: dict[str, str] = params or {}

        self.complete_params()

    def __aiter__(self) -> AsyncIterator[Any]:
        return self

    async def __anext__(self) -> Any:
        try:
            return await self.next_page()
        except errors.PaginatorLastPage:
            raise StopAsyncIteration

    @utils.ratelimit(rps=const.BASE_RPS)
    async def next_page(self) -> Any:
        async with self.session.get(self.url, params=self.params) as response:
            logger.debug(f"Sent GET request [{response.status}]: {response.url}")
            if response.content_type != "application/json":
                raise errors.ResponseContentTypeError(response.content_type)

            data = await response.json()
            logger.debug(f"Response JSON: {data}")
            if not isinstance(data, list):
                data = data.get("data")  # TODO: Add check for api responses (possible errors)
            if not data:
                raise errors.PaginatorLastPage(self.page_number)

            self.page_number += 1
            self.params["page"] = str(self.page_number)
            return self.construct_page(data)

    def complete_params(self) -> None:
        self.params["lang"] = "en"
        if self.page_number is not None:
            self.params["page"] = str(self.page_number)
        if self.limit is not None:
            self.params["limit"] = str(self.limit)

    @abstractmethod
    def construct_page(self, data: Sequence[Mapping]) -> Any:
        pass


class CommentPaginator(BasePaginator):
    def construct_page(self, data: Sequence[Mapping]) -> mdl.CommentPage:
        return mdl.CommentPage(number=self.page_number, data=data)  # type: ignore[arg-type]


class PostPaginator(BasePaginator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
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
        super().__init__(session, url, page_number, limit, params)

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

    def construct_page(self, data: Sequence[Mapping]) -> mdl.PostPage:
        return mdl.PostPage(number=self.page_number, data=data)  # type: ignore[arg-type]


class AIPostPaginator(BasePaginator):
    def construct_page(self, data: Sequence[Mapping]) -> mdl.AIPage:
        return mdl.AIPage(number=self.page_number, data=data)  # type: ignore[arg-type]


class TagPaginator(BasePaginator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
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
        super().__init__(session, url, page_number, limit, params)

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

    def construct_page(self, data: Sequence[Mapping]) -> mdl.TagPage:
        return mdl.TagPage(number=self.page_number, data=data)  # type: ignore[arg-type]


class UserPaginator(BasePaginator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: Optional[int] = None,
        limit: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        params: Optional[dict[str, str]] = None,
        order: Optional[types.UserOrder] = None,
        level: Optional[types.UserLevel] = None
    ) -> None:
        self.order = order
        self.level = level
        super().__init__(session, url, page_number, limit, params)

    def complete_params(self) -> None:
        super().complete_params()
        if self.order is not None:
            self.params["order"] = self.order.value
        if self.level is not None:
            self.params["level"] = str(self.level.value)

    def construct_page(self, data: Sequence[Mapping]) -> mdl.UserPage:
        return mdl.UserPage(number=self.page_number, data=data)  # type: ignore[arg-type]
