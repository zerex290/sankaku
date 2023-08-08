from .http_client import HttpClient
from .clients import *  # noqa: F403


__all__ = [  # noqa: F405
    "HttpClient",
    "PostClient",
    "AIClient",
    "TagClient",
    "BookClient",
    "UserClient",
    "SankakuClient"
]


class SankakuClient(
    PostClient,  # noqa: F405
    AIClient,  # noqa: F405
    TagClient,  # noqa: F405
    BookClient,  # noqa: F405
    UserClient  # noqa: F405
):
    """Simple client for Sankaku API."""
