# Documentation for `posts.py`

::: sankaku.models.posts.GenerationDirectivesAspectRatio
    options:
      show_source: false
      members:
        - type
        - width
        - height

---

::: sankaku.models.posts.GenerationDirectivesRating
    options:
      show_source: false
      members:
        - value
        - default

---

::: sankaku.models.posts.GenerationDirectives
    options:
      show_source: false
      members:
        - tags
        - aspect_ratio
        - rating
        - negative_prompt
        - natural_input
        - denoising_strength

---

::: sankaku.models.posts.AIGenerationDirectives
    options:
      show_source: false
      members:
        - width
        - height
        - prompt
        - batch_size
        - batch_count
        - sampling_steps
        - negative_prompt
        - version

---

::: sankaku.models.posts.BasePost
    options:
      show_source: false
      members:
        - id
        - created_at
        - rating
        - status
        - author
        - file_url
        - preview_url
        - width
        - height
        - file_size
        - file_type
        - extension
        - md5
        - tags

---

::: sankaku.models.posts.Comment
    options:
      show_source: false
      members:
        - id
        - created_at
        - post_id
        - author
        - body
        - score
        - parent_id
        - children
        - deleted
        - deleted_by
        - updated_at
        - can_reply
        - reason

---

::: sankaku.models.posts.Post
    options:
      show_source: false
      members:
        - sample_url
        - sample_width
        - sample_height
        - preview_width
        - preview_height
        - has_children
        - has_comments
        - has_notes
        - is_favorited
        - user_vote
        - parent_id
        - change
        - fav_count
        - recommended_posts
        - recommended_score
        - vote_count
        - total_score
        - comment_count
        - source
        - in_visible_pool
        - is_premium
        - is_rating_locked
        - is_note_locked
        - is_status_locked
        - redirect_to_signup
        - reactions
        - sequence
        - video_duration
        - generation_directives

---

::: sankaku.models.posts.AIPost
    options:
      show_source: false
      members:
        - updated_at
        - post_associated_id
        - generation_directives
