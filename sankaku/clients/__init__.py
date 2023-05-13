from .http_client import HttpClient
from .clients import *


class SankakuClient(  # noqa
    PostClient,
    AIClient,
    TagClient,
    BookClient,
    UserClient
):
    """Simple client for Sankaku API."""
