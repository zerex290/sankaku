from typing import Generic, TypeVar
from dataclasses import dataclass


__all__ = ["Page"]


_T = TypeVar("_T")


@dataclass()
class Page(Generic[_T]):
    """Model that describes page containing content with specific type."""
    number: int
    items: list[_T]
