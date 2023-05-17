# Documentation for sankaku's `enum` types

::: sankaku.types.Rating
    options:
      show_source: false
      members:
        - SAFE
        - QUESTIONABLE
        - EXPLICIT

---

::: sankaku.types.PostOrder
    options:
      show_source: false
      members:
        - POPULARITY
        - DATE
        - QUALITY
        - RANDOM
        - RECENTLY_FAVORITED
        - RECENTLY_VOTED

---

::: sankaku.types.SortParameter
    options:
      show_source: false
      members:
        - NAME
        - TRANSLATIONS
        - TYPE
        - RATING
        - BOOK_COUNT
        - POST_COUNT

---

::: sankaku.types.SortDirection
    options:
      show_source: false
      members:
        - ASC
        - DESC

---

::: sankaku.types.TagOrder
    options:
      show_source: false
      members:
        - POPULARITY
        - QUALITY

---

::: sankaku.types.TagType
    options:
      show_source: false
      members:
        - ARTIST
        - COPYRIGHT
        - CHARACTER
        - MEDIUM
        - META
        - GENRE
        - STUDIO

---

::: sankaku.types.FileType
    options:
      show_source: false
      members:
        - IMAGE
        - GIF
        - VIDEO

---

::: sankaku.types.FileSize
    options:
      show_source: false
      members:
        - LARGE
        - HUGE
        - LONG
        - WALLPAPER
        - A_RATIO_16_9
        - A_RATIO_4_3
        - A_RATIO_3_2
        - A_RATIO_1_1

---

::: sankaku.types.UserOrder
    options:
      show_source: false
      members:
        - POSTS
        - FAVORITES
        - NAME
        - NEWEST
        - OLDEST
        - LAST_SEEN

---

::: sankaku.types.UserLevel
    options:
      show_source: false
      members:
        - ADMIN
        - SYSTEM_USER
        - MODERATOR
        - JANITOR
        - CONTRIBUTOR
        - PRIVILEGED
        - MEMBER
        - BLOCKED
        - UNACTIVATED

---

::: sankaku.types.BookOrder
    options:
      show_source: false
      members:
        - POPULATIRY
        - DATE
        - QUALITY
        - RANDOM
        - RECENTLY_FAVORITED
        - RECENTLY_VOTED