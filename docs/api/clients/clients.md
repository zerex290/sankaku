# Documentation for `clients.py`

::: sankaku.clients.clients.BaseClient
    options:
      members:
        - login

---

::: sankaku.clients.clients.PostClient
    options:
      members:
        - browse_posts
        - get_favorited_posts
        - get_top_posts
        - get_popular_posts
        - get_recommended_posts
        - get_similar_posts
        - get_post_comments
        - get_post

---

::: sankaku.clients.clients.AIClient
    options:
      members:
        - browse_ai_posts
        - get_ai_post

---

::: sankaku.clients.clients.TagClient
    options:
      members:
        - browse_tags
        - get_tag

---

::: sankaku.clients.clients.BookClient
    options:
      members:
        - browse_books
        - get_favorited_books
        - get_recommended_books
        - get_recently_read_books
        - get_related_books
        - get_book

---

:::sankaku.clients.clients.UserClient
    options:
      members:
        - browse_users
        - get_user