from enum import Enum


__all__ = [
    "Rating",
    "PostOrder",
    "SortParameter",
    "SortDirection",
    "TagOrder",
    "TagType",
    "FileType",
    "FileSize",
    "UserOrder",
    "UserLevel",
    "BookOrder"
]


class Rating(str, Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class PostOrder(Enum):
    POPULARITY = "popularity"
    DATE = "date"
    QUALITY = "quality"
    RANDOM = "random"
    RECENTLY_FAVORITED = "recently_favorited"
    RECENTLY_VOTED = "recently_voted"


class SortParameter(Enum):
    NAME = "name"
    TRANSLATIONS = "name_ja"
    TYPE = "type"
    RATING = "rating"
    BOOK_COUNT = "pool_count"
    POST_COUNT = "count"


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class TagOrder(Enum):
    POPULARITY = "popularity"
    QUALITY = "quality"


class TagType(Enum):
    ARTIST = 1
    COPYRIGHT = 3
    CHARACTER = 4
    GENERAL = 0
    MEDIUM = 8
    META = 9
    GENRE = 5
    STUDIO = 2


class FileType(Enum):
    IMAGE = "image"  # jpeg, png, webp formats
    GIF = "gif"  # gif format
    VIDEO = "video"  # mp4, webm formats


class FileSize(Enum):
    LARGE = "large_filesize"
    HUGE = "extremely_large_filesize"
    LONG = "long_image"
    WALLPAPER = "wallpaper"
    A_RATIO_16_9 = "16:9_aspect_ratio"
    A_RATIO_4_3 = "4:3_aspect_ratio"
    A_RATIO_3_2 = "3:2_aspect_ratio"
    A_RATIO_1_1 = "1:1_aspect_ratio"


class UserOrder(Enum):
    POSTS = "post_upload_count"
    FAVORITES = "favorite_count"
    NAME = "name"
    NEWEST = "newest"
    OLDEST = "oldest"
    LAST_SEEN = "active"


class UserLevel(Enum):
    ADMIN = 50
    SYSTEM_USER = 45
    MODERATOR = 40
    JANITOR = 35
    CONTRIBUTOR = 33
    PRIVILEGED = 30
    MEMBER = 20
    BLOCKED = 10
    UNACTIVATED = 0


class BookOrder(Enum):
    POPULARITY = "popularity"
    DATE = "date"
    QUALITY = "quality"
    RANDOM = "random"
    RECENTLY_FAVORITED = "recently_favorited"
    RECENTLY_VOTED = "recently_voted"
