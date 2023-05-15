from aiohttp import ClientSession
from loguru import logger

from .abc import ABCHttpClient
from sankaku import errors, constants as const
from sankaku.models.http import ClientResponse


__all__ = ["HttpClient"]


class HttpClient(ABCHttpClient):
    """HTTP client for API requests that instances use a single session."""
    def __init__(self) -> None:
        self.headers: dict[str, str] = const.HEADERS.copy()
        self.session: ClientSession = ClientSession()

    def __del__(self) -> None:
        if not self.session.closed and self.session.connector is not None:
            self.session.connector.close()

    async def close(self) -> None:
        """There is no need to close client with single session."""

    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make request to specified url."""
        if kwargs.get("headers") is None:
            kwargs["headers"] = self.headers

        response = await self.session.request(method, url, **kwargs)
        logger.debug(f"Sent {method} request to {response.url}")

        if response.content_type != "application/json":
            raise errors.SankakuServerError(
                response.status, "Invalid response content type",
                content_type=response.content_type
            )

        client_response = ClientResponse(
            response.status,
            await response.json(encoding="utf-8"),
        )
        response.close()
        logger.debug(
            f"Request {method} returned response with status "
            f"[{client_response.status}]: {client_response.json}",
        )

        return client_response

    async def get(self, url: str, **kwargs) -> ClientResponse:
        """Send GET request to specified url."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> ClientResponse:
        """Send POST request to specified url."""
        return await self.request("POST", url, **kwargs)
