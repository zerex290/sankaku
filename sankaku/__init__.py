from dataclasses import dataclass

from .clients import SankakuClient


__all__ = ["SankakuClient"]


@dataclass(frozen=True)
class ValueRange:
    min: int
    max: int
