class SankakuError(Exception):
    """Base Error class."""

    msg: str = ""

    def __repr__(self) -> str:
        return self.msg

    def __str__(self) -> str:
        return self.__repr__()


class RateLimitError(SankakuError):
    msg = "Can't set both rps and rpm at once."


class LoginRequirementError(SankakuError):
    msg = "You must be logged-in."


class VideoDurationError(SankakuError):
    msg = "Argument is available only with video files."
