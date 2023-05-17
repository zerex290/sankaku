# Documentation for `users.py`

::: sankaku.models.users.BaseUser
    options:
      show_source: false
      members:
        - id
        - name
        - avatar
        - avatar_rating

---

::: sankaku.models.users.Author
    options:
      show_source: false

---

::: sankaku.models.users.User
    options:
      show_source: false
      members:
        - level
        - upload_limit
        - created_at
        - favs_are_private
        - avatar
        - post_upload_count
        - pool_upload_count
        - comment_count
        - post_update_count
        - note_update_count
        - wiki_update_count
        - forum_post_count
        - pool_update_count
        - series_update_count
        - tag_update_count
        - artist_update_count
        - show_popup_version
        - credits
        - credits_subs
        - is_ai_beta
        - last_logged_in_at
        - favorite_count
        - post_favorite_count
        - pool_favorite_count
        - vote_count
        - post_vote_count
        - pool_vote_count
        - recommended_posts_for_user
        - subscriptions

---

::: sankaku.models.users.ExtendedUser
    options:
      show_source: false
      members:
        - email
        - hide_ads
        - subscription_level
        - filter_content
        - receive_dmails
        - email_verification_status
        - is_verified
        - verifications_count
        - blacklist_is_hidden
        - blacklisted_tags
        - blacklisted
        - mfa_method