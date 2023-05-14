from abc import ABC, abstractmethod
from typing import Optional

from sankaku.models.http import ClientResponse


class ABCHttpClient(ABC):
    """Abstract HTTP client"""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self) -> "ABCHttpClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @abstractmethod
    def __del__(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make request to specified url."""


class ABCClient(ABC):
    """Abstract Sankaku client"""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def login(
        self,
        *,
        access_token: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        pass
