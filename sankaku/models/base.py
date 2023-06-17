import warnings

from pydantic import BaseModel, Extra


__all__ = ["SankakuResponseModel"]


class SankakuResponseModel(BaseModel, extra=Extra.forbid):
    """Base model for sankaku JSON responses."""
