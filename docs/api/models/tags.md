# Documentation for `tags.py`

::: sankaku.models.tags.BaseTag
    options:
      show_source: false
      members:
        - id
        - name
        - name_en
        - name_ja
        - type
        - post_count
        - pool_count
        - series_count
        - rating

---

::: sankaku.models.tags.TagMixin
    options:
      show_source: false
      members:
        - count
        - tag_name
        - total_post_count
        - total_pool_count

---

::: sankaku.models.tags.PostTag
    options:
      show_source: false
      members:
        - locale
        - version

---

::: sankaku.models.tags.NestedTag
    options:
      show_source: false
      members:
        - post_count
        - cached_related
        - cached_related_expires_on
        - type
        - name_en
        - name_ja
        - popularity_all
        - quality_all
        - popularity_ero
        - popularity_safe
        - quality_ero
        - quality_safe
        - parent_tags
        - child_tags
        - pool_count
        - premium_post_count
        - non_premium_post_count
        - premium_pool_count
        - non_premium_pool_count
        - series_count
        - premium_series_count
        - non_premium_series_count
        - is_trained
        - child
        - parent
        - version

---

::: sankaku.models.tags.Translations
    options:
      show_source: false
      members:
        - root_id
        - lang
        - translation

---

::: sankaku.models.tags.PageTag
    options:
      show_source: false
      members:
        - translations
        - related_tags
        - child_tags
        - parent_tags

---

::: sankaku.models.tags.Wiki
    options:
      show_source: false
      members:
        - id
        - title
        - body
        - created_at
        - updated_at
        - author
        - is_locked
        - version

---

::: sankaku.models.tags.WikiTag
    options:
      show_source: false
      members:
        - related_tags
        - child_tags
        - parent_tags
        - alias_tags
        - implied_tags
        - translations
        - wiki