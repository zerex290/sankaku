from abc import ABC, abstractmethod
from typing import Optional

from sankaku.models.http import ClientResponse


__all__ = ["ABCHttpClient", "ABCClient"]


class ABCHttpClient(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Abstract client for handling http requests."""
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @abstractmethod
    def __del__(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close previously created client session."""

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make request to specified url."""


class ABCClient(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Abstract Sankaku client."""
        pass

    @abstractmethod
    async def login(
            self,
            *,
            access_token: Optional[str] = None,
            login: Optional[str] = None,
            password: Optional[str] = None
    ) -> None:
        """Login into sankakucomplex.com via access token or credentials."""
