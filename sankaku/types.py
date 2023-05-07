from enum import Enum


class Rating(str, Enum):
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"


class Order(Enum):
    POPULARITY = "popularity"
    DATE = "date"
    QUALITY = "quality"
    RANDOM = "random"
    RECENTLY_FAVORITED = "recently_favorited"
    RECENTLY_VOTED = "recently_voted"


class Tag(Enum):
    ARTIST = 1
    COPYRIGHT = 3
    CHARACTER = 4
    GENERAL = 0

    MEDIUM = 8
    META = 9
    GENRE = 5
    STUDIO = 2


class File(Enum):
    IMAGE = "image"  # jpeg, png, webp formats
    GIF = "animated_gif"  # gif format
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
