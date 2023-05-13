from abc import ABC, abstractmethod

from sankaku.models.http import ClientResponse


class ABCHttpClient(ABC):
    """Abstract HTTP client"""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> "ABCHttpClient":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

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
    async def login(self, login: str, password: str) -> None:
        pass
