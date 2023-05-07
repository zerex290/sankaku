import asyncio
from functools import wraps
from typing import TypeVar, ParamSpec, Optional
from collections.abc import Callable, Awaitable


from sankaku.errors import RateLimitError


__all__ = ["ratelimit"]


_T = TypeVar("_T")
_P = ParamSpec("_P")


def ratelimit(
    *,
    rps: Optional[int] = None,
    rpm: Optional[int] = None
) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]:
    """
    Limit the number of requests.

    :param rps: Request per second
    :param rpm: Requests per minute
    """
    if all(locals().values()):
        raise RateLimitError
    elif not any(locals().values()):
        raise TypeError("At least argument must be specified.")

    sleep_time: float = (1 / rps) if rps else (60 / rpm)  # type: ignore[operator]

    def wrapper(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
        @wraps(func)
        async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            await asyncio.sleep(sleep_time)
            return await func(*args, **kwargs)
        return inner

    return wrapper
