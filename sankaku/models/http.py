from dataclasses import dataclass
from typing import Any


__all__ = ["ClientResponse"]


@dataclass()
class ClientResponse:
    """Dataclass that preserves information from aiohttp ClientResponse."""
    status: int
    ok: bool
    json: Any
