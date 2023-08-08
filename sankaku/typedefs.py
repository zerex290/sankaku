from dataclasses import dataclass
from typing import Optional

try:
    from typing import TypedDict
except (ImportError, ModuleNotFoundError):
    from typing_extensions import TypedDict


__all__ = ["ValueRange", "Timestamp"]


@dataclass(frozen=True)
class ValueRange:  # noqa: D101
    min: int  # noqa: A003
    max: int  # noqa: A003


class Timestamp(TypedDict):  # noqa: D101
    json_class: str
    s: Optional[int]
    n: int
