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
    msg: str = ""

    def __init__(self, msg: Optional[str] = None) -> None:
        """Base error class for raising exceptions without any special params."""
        self.msg = msg or self.msg

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return str(self.msg)


class RateLimitError(SankakuError):
    msg = "Can't set both rps and rpm at once."


class LoginRequirementError(SankakuError):
    msg = "You must be logged-in."


class VideoDurationError(SankakuError):
    msg = "Argument is available only with video files."


class PaginatorLastPage(SankakuError):  # noqa: N818
    msg = "Last available page reached."


class SankakuServerError(SankakuError):
    def __init__(
        self,
        status: Optional[int],
        msg: Optional[str] = None,
        **kwargs
    ) -> None:
        """Error class for parametrized exceptions."""
        self.status = status
        self.kwargs = kwargs

        str_kwargs = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
        delimiter = ": " if self.kwargs else ""
        self.msg = f"[{self.status}] {msg or self.msg}{delimiter}{str_kwargs}."

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return str(self.msg)


class PageNotFoundError(SankakuServerError):
    msg = "Failed to fetch page with requested params"


class AuthorizationError(SankakuServerError):
    msg = "Authorization failed"
