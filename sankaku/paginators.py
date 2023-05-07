from typing import Optional, Literal, Annotated
from collections.abc import AsyncIterator, Sequence, Mapping
from datetime import datetime

import aiohttp

import sankaku.models as mdl
from . import ValueRange
from sankaku import constants, types, utils, errors


class BasePaginator:
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
        self.params: dict[str, Optional[str]] = {}
        self.limit = limit

    def __aiter__(self) -> AsyncIterator[mdl.posts.BasePage]:
        self._complete_params()
        return self

    @utils.ratelimit(rps=constants.BASE_RPS)
    async def __anext__(self) -> mdl.posts.BasePage:
        async with self.session.get(self.url, params=self.params) as response:
            data = await response.json()
            if not isinstance(data, list):
                data = data.get("data")
            elif not data:
                # Different data means end of search
                await self.session.close()
                raise StopAsyncIteration
            self.page_number += 1
            self.params.update(page=str(self.page_number))
            return self._construct_page(data)

    def _complete_params(self) -> None:
        self.params.update(
            lang="en",
            page=str(self.page_number),
            limit=str(self.limit),
        )

    def _construct_page(self, data: Sequence[Mapping]) -> mdl.posts.BasePage:
        return mdl.posts.BasePage(number=self.page_number, posts=data)  # type: ignore[arg-type]


class PostPaginator(BasePaginator):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: int,
        limit: Annotated[int, ValueRange(1, 100)],
        hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]],
        order_by: Optional[types.Order],
        date: Optional[list[datetime]],
        rating: Optional[types.Rating],
        threshold: Optional[Annotated[int, ValueRange(1, 100)]],
        file_size: Optional[types.FileSize],
        file_type: Optional[types.File],
        video_duration: Optional[list[int]],
        recommended_for: Optional[str],
        favorite_by: Optional[str],
        tags: Optional[list[str]],
        added_by: Optional[list[str]],
        voted: Optional[str]
    ) -> None:
        super().__init__(session, url, page_number, limit)
        self.hide_posts_in_books = hide_posts_in_books
        self.order_by = order_by
        self.date = date
        self.rating = rating
        self.threshold = threshold
        self.file_size = file_size
        self.file_type = file_type
        self.video_duration = video_duration
        self.recommended_for = recommended_for
        self.favorite_by = favorite_by
        self.tags = tags
        self.added_by = added_by
        self.voted = voted

    def _complete_params(self) -> None:
        if self.tags is None:
            self.tags = []

        for k, v in self.__dict__.items():
            if v is None:
                continue
            match k:
                case "order_by":
                    self.tags.append(f"order:{self.order_by.value}")  # type: ignore[union-attr]
                case "date":
                    self.tags.append(
                        "date:"
                        + "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in v)
                    )
                case "rating":
                    self.tags.append(f"rating:{self.rating.value}")  # type: ignore[union-attr]
                case "threshold":
                    self.tags.append(f"threshold:{self.threshold}")
                case "file_size":
                    self.tags.append(self.file_size.value)  # type: ignore[union-attr]
                case "file_type":
                    if self.file_type == types.File.IMAGE:
                        continue
                    self.tags.append(f"file_type:{self.file_type.value}")  # type: ignore[union-attr]
                case "video_duration":
                    if self.file_type != types.File.VIDEO:
                        raise errors.VideoDurationError
                    self.tags.append(
                        "duration:"
                        + "..".join(str(s) for s in self.video_duration)  # type: ignore[union-attr]
                    )
                case "recommended_for":
                    self.tags.append(f"recommended_for:{self.recommended_for}")
                case "favorite_by":
                    self.tags.append(f"fav:{self.favorite_by}")
                case "added_by":
                    for user in self.added_by:  # type: ignore[union-attr]
                        self.tags.append(f"user:{user}")
                case "voted":
                    self.tags.append(f"voted:{self.voted}")
                case _:
                    continue

        if self.hide_posts_in_books is not None:
            self.params.update(hide_posts_in_books=self.hide_posts_in_books)
        if self.tags:
            self.params.update(tags=" ".join(self.tags))
        super()._complete_params()

    def _construct_page(self, data: Sequence[Mapping]) -> mdl.posts.Page:
        return mdl.posts.Page(number=self.page_number, posts=data)  # type: ignore[arg-type]


class AIPostPaginator(BasePaginator):
    def _complete_params(self) -> None:
        super()._complete_params()

    def _construct_page(self, data: Sequence[Mapping]) -> mdl.posts.AIPage:
        return mdl.posts.AIPage(number=self.page_number, posts=data)  # type: ignore[arg-type]
