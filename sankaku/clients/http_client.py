import os
from typing import Dict, Optional

from aiohttp import ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from loguru import logger

from sankaku import errors, constants as const
from sankaku.constants import BASE_RETRIES
from sankaku.models.http import ClientResponse
from .abc import ABCHttpClient


try:
    from aiohttp_socks import ProxyConnector as SocksProxyConnector  # type: ignore
except (ImportError, ModuleNotFoundError):
    SocksProxyConnector = None


__all__ = ["HttpClient"]


def _get_socks_connector() -> Optional[SocksProxyConnector]:  # type: ignore
    if SocksProxyConnector is None:
        return None

    proxy = os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")  # noqa: E501
    if proxy is None or not proxy.startswith("socks"):
        return None

    return SocksProxyConnector.from_url(proxy)


class HttpClient(ABCHttpClient):
    def __init__(self) -> None:
        """HTTP client for API requests that instances use a single session."""
        self.headers: Dict[str, str] = const.HEADERS.copy()

        socks_connector = _get_socks_connector()
        if socks_connector is not None:
            # use socks connector
            kwargs = {"connector": socks_connector}
        else:
            # aiohttp will read HTTP_PROXY and HTTPS_PROXY from env
            kwargs = {"trust_env": True}
        self._client_session: ClientSession = ClientSession(**kwargs)  # type: ignore

        retry_options = ExponentialRetry(attempts=BASE_RETRIES)
        self.session: RetryClient = RetryClient(
            raise_for_status=False,
            retry_options=retry_options,
            client_session=self._client_session
        )

    def __del__(self) -> None:
        if not self._client_session.closed and self._client_session.connector is not None:  # noqa: E501
            self._client_session.connector.close()

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
            response.ok,
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
