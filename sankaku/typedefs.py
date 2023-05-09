from dataclasses import dataclass


@dataclass(frozen=True)
class ValueRange:
    min: int
    max: int
