from typing import Optional


class SankakuError(Exception):
    """Base error class for raising exceptions without any special params."""

    msg: str = ""

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return self.msg


class RateLimitError(SankakuError):
    msg = "Can't set both rps and rpm at once."


class LoginRequirementError(SankakuError):
    msg = "You must be logged-in."


class VideoDurationError(SankakuError):
    msg = "Argument is available only with video files."


class SankakuServerError(SankakuError):
    """Error class for parametrized exceptions."""

    def __init__(
            self,
            status: Optional[int],
            msg: Optional[str] = None,
            **kwargs
    ) -> None:
        str_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        delimiter = ": " if kwargs else ""
        self.msg = f"[{status}] {msg or self.msg}{delimiter}{str_kwargs}."

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return self.msg


class PaginatorLastPage(SankakuServerError):
    msg = "Last available page reached"


class PageNotFoundError(SankakuServerError):
    msg = f"Failed to fetch page with requested params"


class AuthorizationError(SankakuServerError):
    msg = f"Authorization failed"
