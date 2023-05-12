from typing import Generic, TypeVar
from dataclasses import dataclass


__all__ = ["Page"]


_T = TypeVar("_T")


@dataclass()
class Page(Generic[_T]):
    number: int
    items: list[_T]
