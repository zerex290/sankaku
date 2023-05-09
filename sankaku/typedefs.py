from dataclasses import dataclass
from typing import TypedDict, Optional


__all__ = ["ValueRange", "Timestamp"]


@dataclass(frozen=True)
class ValueRange:
    min: int
    max: int


class Timestamp(TypedDict):
    json_class: str
    s: Optional[int]
    n: int
