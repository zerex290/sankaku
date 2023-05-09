import os
import asyncio

import pytest  # noqa

from sankaku.clients import SankakuClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def nlclient() -> SankakuClient:
    """Client without performed authorization."""

    return SankakuClient()


@pytest.fixture(scope="module")
async def lclient() -> SankakuClient:
    """Client where authorization is performed."""

    client = SankakuClient()
    await client.login(os.getenv("LOGIN"), os.getenv("PASSWORD"))
    return client
