from dataclasses import dataclass
from typing import Any


__all__ = ["ClientResponse"]


@dataclass()
class ClientResponse:
    """Dataclass that preserves information from aiohttp ClientResponse."""
    status: int
    json: Any

    @property
    def ok(self) -> bool:
        """Check if response status code is less than 400."""
        return self.status < 400
