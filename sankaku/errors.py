from typing import Optional


class SankakuError(Exception):
    """Base Error class."""

    msg: str = ""

    def __init__(
        self,
        msg: Optional[str] = None,
        error_id: Optional[str] = None,
        code: Optional[str] = None,
        kwargs: Optional[dict] = None
    ) -> None:
        self.error_id = error_id
        self.code = code
        self.kwargs = kwargs or {}

        str_kwargs = " | ".join(f"{k}={v}" for k, v in self.kwargs.items())
        sep = ": " if self.kwargs else ""
        self.msg = msg or f"[{self.error_id}] {self.code}{sep}{str_kwargs}."

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return self.msg


class PaginatorLastPage(SankakuError):
    def __init__(self, page_number: int):
        self.msg = f"Reached last available page [{page_number}]."


class RateLimitError(SankakuError):
    msg = "Can't set both rps and rpm at once."


class LoginRequirementError(SankakuError):
    msg = "You must be logged-in."


class VideoDurationError(SankakuError):
    msg = "Argument is available only with video files."


class PostNotFoundError(SankakuError):
    def __init__(self, post_id: int) -> None:
        self.msg = f"Failed to find post with id {post_id}."


class TagNotFoundError(SankakuError):
    def __init__(self, name_or_id: str | int) -> None:
        self.msg = (
            f"Failed to find tag with "
            f"{'name' if isinstance(name_or_id, str) else 'id'} "
            f"{name_or_id}."
        )


class UserNotFoundError(SankakuError):
    def __init__(self, name_or_id: str | int) -> None:
        self.msg = (
            f"Failed to find user with "
            f"{'name' if isinstance(name_or_id, str) else 'id'} "
            f"{name_or_id}."
        )


class AuthorizationError(SankakuError):
    def __init__(self, status: int, error: str) -> None:
        self.msg = f"Authorization failed with status code {status}: {error}."
