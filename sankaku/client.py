import json
from typing import Optional, Literal, Annotated, Self
from collections.abc import AsyncIterator
from datetime import datetime

import aiohttp

import sankaku.models as mdl
from . import ValueRange
from sankaku import constants, types, utils, errors


class PostsPaginator:
    def __init__(
        self,
        session: aiohttp.ClientSession,
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
        self.session = session
        self.page_number = page_number
        self.params: dict[str, Optional[str]] = {}

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
        self.favorite_by = favorite_by
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
                        + "..".join(d.strftime("%Y-%m-%dT%H:%M") for d in v)
                    )
                case "rating":
                    self.tags.append(f"rating:{self.rating.value}")
                case "threshold":
                    self.tags.append(f"threshold:{self.threshold}")
                case "file_size":
                    self.tags.append(self.file_size.value)
                case "file_type":
                    if self.file_type == types.File.IMAGE:
                        continue
                    self.tags.append(f"file_type:{self.file_type.value}")
                case "video_duration":
                    if self.file_type != types.File.VIDEO:
                        raise errors.VideoDurationError
                    self.tags.append(
                        "duration:"
                        + "..".join(str(s) for s in self.video_duration)
                    )
                case "recommended_for":
                    self.tags.append(f"recommended_for:{self.recommended_for}")
                case "favorite_by":
                    self.tags.append(f"fav:{self.favorite_by}")
                case "added_by":
                    for user in self.added_by:
                        self.tags.append(f"user:{user}")
                case "voted":
                    self.tags.append(f"voted:{self.voted}")
                case _:
                    continue

        if self.hide_posts_in_books is not None:
            self.params.update(hide_posts_in_books=self.hide_posts_in_books)
        if self.tags:
            self.params.update(tags=" ".join(self.tags))
        self.params.update(
            lang="en",
            page=str(self.page_number),
            limit=str(self.limit),
        )

    def __aiter__(self) -> AsyncIterator[mdl.post.Page]:
        return self

    @utils.rate_limit(rps=constants.BASE_RPS)
    async def __anext__(self) -> mdl.post.Page:
        async with self.session.get(
            constants.POST_BROWSE_URL,
            params=self.params,
        ) as response:
            data = await response.json()
            if not isinstance(data, list) or not data:
                # Different data means end of search
                await self.session.close()
                raise StopAsyncIteration
            page = mdl.post.Page(number=self.page_number, posts=data)
            self.page_number += 1
            self.params.update(page=str(self.page_number))
            return page


class BaseClient:
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
        self.profile: Optional[mdl.user.ExtendedProfile] = None
        self.access_token: str = ""
        self.refresh_token: str = ""
        self._token_type: str = ""

    @utils.rate_limit(rps=constants.BASE_RPS)
    async def login(self, login: str, password: str) -> Self:
        """
        Login into sankakucomplex.com via login and password.

        :param login: User email or username
        :param password: User password
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.LOGIN_URL,
                headers=self.get_headers(),
                data=json.dumps({"login": login, "password": password})
            ) as response:
                data = await response.json()

                if not response.ok:
                    msg = f"Authorization failed [{response.status}]: {data}"
                    raise ValueError(msg)

                self._token_type = data["token_type"]
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]

                self.profile = mdl.user.ExtendedProfile(**data["current_user"])
        return self

    def get_headers(self, *, auth: bool = False) -> dict[str, str]:
        headers = self._HEADERS.copy()
        if auth and not all(self.__dict__.values()):
            raise errors.LoginRequirementError
        elif auth:
            headers["authorization"] = f"{self._token_type} {self.access_token}"
        return headers


class PostClient(BaseClient):
    async def browse_posts(
        self,
        auth: bool = False,
        page_number: int = 1,
        limit: Annotated[int, ValueRange(1, 100)] = 40,
        hide_posts_in_books: Optional[Literal["in-larger-tags", "always"]] = None,
        order_by: Optional[types.Order] = None,
        date: Optional[list[datetime]] = None,
        rating: Optional[types.Rating] = None,
        threshold: Optional[Annotated[int, ValueRange(1, 100)]] = None,
        file_size: Optional[types.FileSize] = None,
        file_type: Optional[types.File] = None,
        video_duration: Optional[list[int]] = None,
        recommended_for: Optional[str] = None,
        favorite_by: Optional[str] = None,
        tags: Optional[list[str]] = None,
        added_by: Optional[list[str]] = None,
        voted: Optional[str] = None
    ) -> AsyncIterator[mdl.post.Post]:
        """
        Iterate through the post browser.

        :param auth: Whether to make request on behalf of currently logged-in user
        :param page_number: Current page number
        :param limit: Maximum amount of posts per page
        :param hide_posts_in_books: Whether show post from books or not
        :param order_by: Posts order rule
        :param date: Date or range of dates
        :param rating: Post rating
        :param threshold: Vote (quality) filter of posts
        :param file_size: Size (aspect ratio) of mediafile
        :param file_type: Type of mediafile in post
        :param video_duration: Video duration in seconds or in range of seconds
        :param recommended_for: Display posts recommended for specified user
        :param favorite_by: Users added post to their favourites
        :param tags: Tags available for search
        :param added_by: Posts uploaded by specified user
        :param voted: Posts voted by specified user
        :return: Asynchronous generator which yields posts
        """
        kwargs = locals().copy()
        del kwargs["self"]
        del kwargs["auth"]
        async for page in PostsPaginator(
            aiohttp.ClientSession(headers=self.get_headers(auth=auth)),
            **kwargs
        ):
            for post in page.posts:
                yield post

    async def get_favorited_posts(self) -> AsyncIterator[mdl.post.Post]:
        """Shorthand way to get favorite posts of currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError
        async for post in self.browse_posts(auth=True, favorite_by=self.profile.name):
            yield post

    async def get_top_posts(self, auth: bool = False) -> AsyncIterator[mdl.post.Post]:
        """
        Shorthand way to get top posts.

        :param auth: Whether to make request on behalf of currently logged-in user
        """
        async for post in self.browse_posts(auth=auth, order_by=types.Order.QUALITY):
            yield post

    async def get_popular_posts(self, auth: bool = False) -> AsyncIterator[mdl.post.Post]:
        """
        Shorthand way to get popular posts.

        :param auth: Whether to make request on behalf of currently logged-in user
        """
        async for post in self.browse_posts(auth=auth, order_by=types.Order.POPULARITY):
            yield post

    async def get_recommended_posts(self) -> AsyncIterator[mdl.post.Post]:
        """Shorthand way to get recommended posts for the currently logged-in user."""

        if self.profile is None:
            raise errors.LoginRequirementError
        async for post in self.browse_posts(auth=True, recommended_for=self.profile.name):
            yield post

    async def get_post(self, post_id: int, auth: bool = False) -> mdl.post.Post:
        posts: list[mdl.post.Post] = []
        async for post in self.browse_posts(auth=auth, tags=[f"id_range:{post_id}"]):
            posts.append(post)
        if not posts:
            raise errors.PostNotFoundError(post_id)
        return posts[0]


class BookClient(BaseClient):
    async def get_recommended_books(self):  # TODO: TBA
        """Shorthand way to get recommended books for the currently logged-in user."""

        raise NotImplementedError


class UserClient(BaseClient):
    async def get_user(self, username: str):
        raise NotImplementedError


class SankakuClient(PostClient):  # noqa
    """Simple client for Sankaku API."""
