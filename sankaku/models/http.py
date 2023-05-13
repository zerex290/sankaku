from dataclasses import dataclass
from typing import Any


@dataclass()
class ClientResponse:
    """Dataclass that preserves information from aiohttp ClientResponse."""

    status: int
    json: Any

    @property
    def ok(self) -> bool:
        return self.status < 400
