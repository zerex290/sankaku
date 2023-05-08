class SankakuError(Exception):
    """Base Error class."""

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


class PostNotFoundError(SankakuError):
    def __init__(self, post_id: int) -> None:
        self.msg = f"Failed to find post with id {post_id}."


class AuthorizationError(SankakuError):
    def __init__(self, status: int, error: str) -> None:
        self.msg = f"Authorization failed with status code {status}: {error}."
