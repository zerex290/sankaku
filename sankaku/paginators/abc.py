from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from sankaku import errors
from sankaku.models import Page


_T = TypeVar("_T")


class ABCPaginator(ABC, Generic[_T]):
    """Abstract paginator class."""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __aiter__(self) -> AsyncIterator[Page[_T]]:
        return self

    async def __anext__(self) -> Page[_T]:
        try:
            return await self.next_page()
        except errors.PaginatorLastPage:
            raise StopAsyncIteration

    @abstractmethod
    async def next_page(self) -> Page[_T]:
        pass

    @abstractmethod
    def complete_params(self) -> None:
        """Complete params passed to paginator for further use."""

    @abstractmethod
    def construct_page(self, data: list[dict]) -> Page[_T]:
        """Construct and return page model."""
