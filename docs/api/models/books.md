# Documentation for `books.py`

::: sankaku.models.books.BookState
    options:
      show_source: false
      members:
        - current_page
        - sequence
        - post_id
        - series_id
        - created_at
        - updated_at
        - percent

---

::: sankaku.models.books.PageBook
    options:
      show_source: false
      members:
        - id
        - name_en
        - name_ja
        - description
        - description_en
        - description_ja
        - created_at
        - updated_at
        - author
        - is_public
        - is_active
        - is_flagged
        - post_count
        - pages_count
        - visible_post_count
        - is_intact
        - rating
        - parent_id
        - has_children
        - is_rating_locked
        - fav_count
        - vote_count
        - total_score
        - comment_count
        - tags
        - post_tags
        - artist_tags
        - genre_tags
        - is_favorited
        - user_vote
        - posts
        - file_url
        - sample_url
        - preview_url
        - cover_post
        - reading
        - is_premium
        - is_pending
        - is_raw
        - is_trial
        - redirect_to_signup
        - locale
        - is_deleted
        - cover_post_id
        - name
        - parent_pool

---

::: sankaku.models.books.Book
    options:
      show_source: false
      members:
        - child_pools
        - flagged_by_user
        - prem_post_count