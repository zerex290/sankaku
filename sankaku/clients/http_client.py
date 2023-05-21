import asyncio
import os
from typing import Dict

from aiohttp import ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from loguru import logger

from sankaku import errors, constants as const
from sankaku.constants import BASE_RETRIES
from sankaku.models.http import ClientResponse
from .abc import ABCHttpClient

__all__ = ["HttpClient"]

try:
    from aiohttp_socks import ProxyConnector as SocksProxyConnector
except (ImportError, ModuleNotFoundError):
    SocksProxyConnector = None


def _get_socks_connector():
    if SocksProxyConnector is not None:
        proxy = os.environ.get('ALL_PROXY') or os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        if proxy.startswith('socks'):
            return SocksProxyConnector.from_url(proxy)
        else:
            return None
    else:
        return None


class HttpClient(ABCHttpClient):
    """HTTP client for API requests that instances use a single session."""

    def __init__(self) -> None:
        self.headers: Dict[str, str] = const.HEADERS.copy()
        socks_connector = _get_socks_connector()
        if socks_connector:
            # use socks connector
            kwargs = {'connector': socks_connector}
        else:
            # use trust env option, aiohttp will read HTTP_PROXY and HTTPS_PROXY from env
            kwargs = {'trust_env': True}
        client_session: ClientSession = ClientSession(**kwargs)

        retry_options = ExponentialRetry(attempts=BASE_RETRIES)
        self.session: RetryClient = RetryClient(
            raise_for_status=False,
            retry_options=retry_options,
            client_session=client_session
        )

    def __del__(self) -> None:
        asyncio.run(self.session.close())

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
