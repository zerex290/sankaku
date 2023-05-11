class SankakuError(Exception):
    """Base Error class."""

    msg: str = ""

    def __repr__(self) -> str:
        return repr(self.msg)

    def __str__(self) -> str:
        return self.msg


class ResponseContentTypeError(SankakuError):
    def __init__(self, content_type: str):
        self.msg = f"Response content type is invalid: {content_type}"


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


class AuthorizationError(SankakuError):
    def __init__(self, status: int, error: str) -> None:
        self.msg = f"Authorization failed with status code {status}: {error}."
