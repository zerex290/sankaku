from .http_client import HttpClient
from .clients import *


__all__ = [
    "HttpClient",
    "PostClient",
    "AIClient",
    "TagClient",
    "BookClient",
    "UserClient",
    "SankakuClient"
]


class SankakuClient(  # noqa
    PostClient,
    AIClient,
    TagClient,
    BookClient,
    UserClient
):
    """Simple client for Sankaku API."""
