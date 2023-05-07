class SankakuError(Exception):
    """Base Error class."""


class RateLimitError(SankakuError):
    def __repr__(self) -> str:
        return f"Can't set both rps and rpm at once."

    def __str__(self) -> str:
        return self.__repr__()
