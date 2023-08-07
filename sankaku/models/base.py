from pydantic import BaseModel


__all__ = ["SankakuResponseModel"]


class SankakuResponseModel(BaseModel, extra="forbid"):
    """Base model for sankaku JSON responses."""
