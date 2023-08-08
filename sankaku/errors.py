from typing import Optional


__all__ = [
    "SankakuError",
    "RateLimitError",
    "LoginRequirementError",
    "VideoDurationError",
    "SankakuServerError",
    "PaginatorLastPage",
    "PageNotFoundError",
    "AuthorizationError"
]


class SankakuError(Exception):
    """Base error class for raising exceptions without any special params."""
    msg: str = ""

    def __init__(self, msg: Optional[str] = None) -> None:
        self.msg = msg or self.msg

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return str(self.msg)


class RateLimitError(SankakuError):  # noqa: D101
    msg = "Can't set both rps and rpm at once."


class LoginRequirementError(SankakuError):  # noqa: D101
    msg = "You must be logged-in."


class VideoDurationError(SankakuError):  # noqa: D101
    msg = "Argument is available only with video files."


class PaginatorLastPage(SankakuError):  # noqa: D101, N818
    msg = "Last available page reached."


class SankakuServerError(SankakuError):
    """Error class for parametrized exceptions."""
    def __init__(
        self,
        status: Optional[int],
        msg: Optional[str] = None,
        **kwargs
    ) -> None:
        self.status = status
        self.kwargs = kwargs

        str_kwargs = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
        delimiter = ": " if self.kwargs else ""
        self.msg = f"[{self.status}] {msg or self.msg}{delimiter}{str_kwargs}."

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return str(self.msg)


class PageNotFoundError(SankakuServerError):  # noqa: D101
    msg = "Failed to fetch page with requested params"


class AuthorizationError(SankakuServerError):  # noqa: D101
    msg = "Authorization failed"
