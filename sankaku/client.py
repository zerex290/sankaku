import json
from typing import Optional, Literal, Annotated
from collections.abc import AsyncIterator
from datetime import datetime
from dataclasses import dataclass

import aiohttp

from sankaku import constants, types
from sankaku.models.user import Profile
from sankaku.models.post import Page


@dataclass(frozen=True)
class ValueRange:
    min: int
    max: int


class LoginError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code: int = code
        self.message: str = message

    def __repr__(self) -> str:
        return f"Authorization failed [{self.code}]: {self.message}"


class PostsPaginator:
    def __init__(
            self, session: aiohttp.ClientSession,
            limit: Annotated[int, ValueRange(1, 100)],
            hide_posts_in_books: Literal["in-larger-tags", "always"] = "in-larger-tags",
            order_by: Optional[types.Order] = None,
            date: Optional[list[datetime]] = None,
            rating: Optional[types.Rating] = None,
            threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
            file_size: Optional[types.FileSize] = None,
            file_type: Optional[types.File] = None,
            video_duration: Optional[list[int]] = None,
            recommended_for: Optional[str] = None,
            favourite_by: Optional[str] = None,
            tags: Optional[list[str]] = None,
            added_by: Optional[list[str]] = None,
            voted: Optional[str] = None
    ) -> None:
        self.session = session
        self.next: Optional[str] = ""
        self.params: dict[str, Optional[str]] = {"next": self.next, "lang": "en"}

        self.limit = limit
        self.hide_posts_in_books = hide_posts_in_books
        self.order_by = order_by
        self.date = date
        self.rating = rating
        self.threshold = threshold
        self.file_size = file_size
        self.file_type = file_type
        self.video_duration = video_duration
        self.recommended_for = recommended_for
        self.favourite_by = favourite_by
        self.tags = tags
        self.added_by = added_by
        self.voted = voted

        self.complete_params()

    def complete_params(self) -> None:
        if self.tags is None:
            self.tags = []

        for k, v in self.__dict__.items():
            if v is None:
                continue
            match k:
                case "order_by":
                    self.tags.append(f"order:{self.order_by.value}")
                case "date":
                    self.tags.append(
                        "date:"
                        "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in v)
                    )
                case "rating":  # TODO: protect from undefined rating
                    self.tags.append(f"rating:{self.rating.value}")
                case "threshold":
                    self.tags.append(f"threshold:{self.threshold}")
                case "file_size":
                    self.tags.append(self.file_size.value)
                case "file_type":  # TODO: make image enum unavailable
                    self.tags.append(f"file_type:{self.file_type.value}")
                case "video_duration":  # TODO: make availability only with videos
                    self.tags.append(
                        "duration:"
                        + "..".join(str(s) for s in self.video_duration)
                    )
                case "recommended_for":
                    self.tags.append(f"recommended_for:{self.recommended_for}")
                case "favourite_by":
                    self.tags.append(f"fav:{self.favourite_by}")
                case "added_by":
                    for user in self.added_by:
                        self.tags.append(f"user:{user}")
                case "voted":
                    self.tags.append(f"voted:{self.voted}")
                case _:
                    continue

            self.params.update(
                limit=str(self.limit),
                hide_posts_in_books=self.hide_posts_in_books,
                tags=" ".join(self.tags)
            )

    def __aiter__(self) -> AsyncIterator[Page]:
        return self

    async def __anext__(self) -> Page:
        if self.next is None:
            await self.session.close()
            raise StopAsyncIteration

        async with self.session.get(
                constants.POST_BROWSE_URL,
                params=self.params,
        ) as response:
            page = Page(**(await response.json()))
            self.params.update(next=page.meta.next)
            self.next = page.meta.next
            return page


class SankakuClient:
    _headers: dict[str] = {
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
        self.profile: Optional[Profile] = None
        self.access_token: str = ""
        self.refresh_token: str = ""
        self._token_type: str = ""

    async def login(self, login: str, password: str) -> "SankakuClient":
        """
        Login into sankakucomplex.com via login and password.

        :param login: User email or username
        :param password: User password
        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    constants.LOGIN_URL,
                    headers=self._get_headers(),
                    data=json.dumps({"login": login, "password": password})
            ) as response:
                data = await response.json()

                if not response.ok:
                    raise LoginError(response.status, data)

                self._token_type = data["token_type"]
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]

                self.profile = Profile(**data["current_user"])
        return self

    async def browse_pages(
            self,
            limit: Annotated[int, ValueRange(1, 100)],
            hide_posts_in_books: Literal["in-larger-tags", "always"] = "in-larger-tags",
            order_by: Optional[types.Order] = None,
            date: Optional[list[datetime]] = None,
            rating: Optional[types.Rating] = None,
            threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
            file_size: Optional[types.FileSize] = None,
            file_type: Optional[types.File] = None,
            video_duration: Optional[list[int]] = None,
            recommended_for: Optional[str] = None,
            favourite_by: Optional[str] = None,
            tags: Optional[list[str]] = None,
            added_by: Optional[list[str]] = None,
            voted: Optional[str] = None
    ) -> PostsPaginator:
        """
        Iterate through posts browser.

        :param limit: Maximum amount of posts per page
        :param hide_posts_in_books: Whether show post from books or not
        :param order_by: Posts order rule
        :param date: Date or range of dates
        :param rating: Post rating
        :param threshold: Vote (quality) filter of posts
        :param file_size: Size (aspect ratio) of mediafile
        :param file_type: Type of mediafile in post
        :param video_duration: Video duration in seconds or in range of seconds
        :param recommended_for: IDK what it actually means...  # TODO: fix desc
        :param favourite_by: Users added post to their favourites
        :param tags: Tags, available for search (max 4 for logged in users)
        :param added_by: Posts uploaded by specified user
        :param voted: Posts voted by specified user
        :return: Asynchronous iterator
        """
        kwargs = locals().copy()
        del kwargs["self"]
        return PostsPaginator(
            aiohttp.ClientSession(headers=self._get_headers(auth=True)),
            **kwargs
        )

    def _get_headers(self, *, auth: bool = False) -> dict[str]:
        headers = self._headers.copy()
        if auth:
            headers["authorization"] = f"{self._token_type} {self.access_token}"
        return headers
