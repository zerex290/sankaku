from dataclasses import dataclass
from typing import Generic, TypeVar, List


__all__ = ["Page"]

_T = TypeVar("_T")


@dataclass()
class Page(Generic[_T]):
    """Model that describes page containing content with specific type."""
    number: int
    items: List[_T]
