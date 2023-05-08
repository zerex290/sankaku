from abc import ABC, abstractmethod
from typing import Optional, Literal, Annotated, Any
from collections.abc import AsyncIterator, Sequence, Mapping
from datetime import datetime

import aiohttp

import sankaku.models as mdl
from . import ValueRange
from sankaku import constants, types, utils, errors


__all__ = ["PostPaginator", "AIPostPaginator", "TagPaginator"]


class BasePaginator(ABC):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: int,
        limit: Annotated[int, ValueRange(1, 100)],
    ) -> None:
        self.session = session
        self.url = url
        self.page_number = page_number
        self.limit = limit
        self.params: dict[str, Optional[str]] = {}

    def __aiter__(self) -> AsyncIterator[Any]:
        self._complete_params()
        return self

    @utils.ratelimit(rps=constants.BASE_RPS)
    async def __anext__(self) -> Any:
        async with self.session.get(self.url, params=self.params) as response:
            data = await response.json()
            if not isinstance(data, list):
                data = data.get("data")
            if not data:
                # Different data means end of search
                await self.session.close()
                raise StopAsyncIteration
            self.page_number += 1
            self.params.update(page=str(self.page_number))
            return self.construct_page(data)

    def _complete_params(self) -> None:
        self.params.update(
            lang="en",
            page=str(self.page_number),
            limit=str(self.limit),
        )

    @abstractmethod
    def construct_page(self, data: Sequence[Mapping]) -> Any:
        pass


class PostPaginator(BasePaginator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: int,
        limit: Annotated[int, ValueRange(1, 100)],
        hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]],
        order: Optional[types.Order],
        date: Optional[list[datetime]],
        rating: Optional[types.Rating],
        threshold: Optional[Annotated[int, ValueRange(1, 100)]],
        file_size: Optional[types.FileSize],
        file_type: Optional[types.File],
        video_duration: Optional[list[int]],
        recommended_for: Optional[str],
        favorited_by: Optional[str],
        tags: Optional[list[str]],
        added_by: Optional[list[str]],
        voted: Optional[str]
    ) -> None:
        super().__init__(session, url, page_number, limit)
        self.hide_posts_in_books = hide_posts_in_books
        self.order = order
        self.date = date
        self.rating = rating
        self.threshold = threshold
        self.file_size = file_size
        self.file_type = file_type
        self.video_duration = video_duration
        self.recommended_for = recommended_for
        self.favorited_by = favorited_by
        self.tags = tags
        self.added_by = added_by
        self.voted = voted

    def _complete_params(self) -> None:
        if self.tags is None:
            self.tags = []

        for items in self.__dict__.items():
            match items:
                case [_, None]:
                    continue
                case ["rating" | "order" | "file_type" as k, v] if v != types.File.IMAGE:
                    self.tags.append(f"{k}:{v.value}")
                case ["threshold" | "recommended_for" | "voted" as k, v]:
                    self.tags.append(f"{k}:{v}")
                case ["file_size", _]:
                    self.tags.append(self.file_size.value)  # type: ignore[union-attr]
                case ["date", _]:
                    date = "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in self.date)  # type: ignore[union-attr]
                    self.tags.append(f"date:{date}")
                case ["video_duration", _] if self.file_type != types.File.VIDEO:
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
            self.params.update(hide_posts_in_books=self.hide_posts_in_books)
        if self.tags:
            self.params.update(tags=" ".join(self.tags))
        super()._complete_params()

    def construct_page(self, data: Sequence[Mapping]) -> mdl.Page:
        return mdl.Page(number=self.page_number, data=data)  # type: ignore[arg-type]


class AIPostPaginator(BasePaginator):
    def construct_page(self, data: Sequence[Mapping]) -> mdl.AIPage:
        return mdl.AIPage(number=self.page_number, data=data)  # type: ignore[arg-type]


class TagPaginator(BasePaginator):
    def construct_page(self, data: Sequence[Mapping]) -> mdl.TagPage:
        return mdl.TagPage(number=self.page_number, data=data)  # type: ignore[arg-type]
