"""Miscellaneous support functions that are used at different places."""

import asyncio
from datetime import datetime
from functools import wraps
from typing import TypeVar, Optional, Callable, Awaitable

from typing_extensions import ParamSpec

from sankaku.errors import RateLimitError
from sankaku.typedefs import Timestamp


__all__ = ["ratelimit", "convert_ts_to_datetime"]

_T = TypeVar("_T")
_P = ParamSpec("_P")


def ratelimit(
        *,
        rps: Optional[int] = None,
        rpm: Optional[int] = None
) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]:
    """Limit the number of requests.

    Args:
        rps: Request per second
        rpm: Requests per minute
    """
    if all(locals().values()):
        raise RateLimitError
    elif not any(locals().values()):
        raise TypeError("At least one argument must be specified.")

    sleep_time: float = (1 / rps) if rps else (60 / rpm)  # type: ignore

    def wrapper(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
        @wraps(func)
        async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            await asyncio.sleep(sleep_time)
            return await func(*args, **kwargs)

        return inner

    return wrapper


def convert_ts_to_datetime(ts: Timestamp) -> Optional[datetime]:
    """Convert timestamp in datetime dict into datetime class."""
    if ts.get("s") is None:
        return None
    return datetime.utcfromtimestamp(ts["s"]).astimezone()  # type: ignore
