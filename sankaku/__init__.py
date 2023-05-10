from loguru import logger

from .clients import SankakuClient


__all__ = ["SankakuClient"]


logger.disable("sankaku")
