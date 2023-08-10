"""Necessary constants such as hardcoded headers, API urls and endpoints,
default values of parameters etc.
"""
from typing import Dict

HEADERS: Dict[str, str] = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 "
        "Yowser/2.5 Safari/537.36"
    ),
    "content-type": "application/json; charset=utf-8",
    "x-requested-with": "com.android.browser",
    "accept-encoding": "gzip, deflate, br",
    "host": "capi-v2.sankakucomplex.com"
}

BASE_URL = "https://login.sankakucomplex.com"
API_URL = "https://capi-v2.sankakucomplex.com"

LOGIN_URL = f"{BASE_URL}/auth/token"
POSTS_URL = f"{API_URL}/posts"
AI_POSTS_URL = f"{API_URL}/ai_posts"
TAGS_URL = f"{API_URL}/tags"
BOOKS_URL = f"{API_URL}/pools"
USERS_URL = f"{API_URL}/users"
PROFILE_URL = f"{USERS_URL}/me"

# Not fully completed urls for usage with str.format()
COMMENTS_URL = f"{POSTS_URL}/{{post_id}}/comments"
RELATED_BOOKS_URL = f"{API_URL}/post/{{post_id}}/pools"
POST_URL = f"{POSTS_URL}/{{post_id}}"
AI_POST_URL = f"{AI_POSTS_URL}/{{post_id}}"
TAG_WIKI_URL = f"{API_URL}/tag-and-wiki{{ref}}/{{name_or_id}}"
BOOK_URL = f"{BOOKS_URL}/{{book_id}}"
USER_URL = f"{USERS_URL}{{ref}}/{{name_or_id}}"

BASE_RPS = 3
BASE_RPM = 180

BASE_RANGE_START = 0
BASE_RANGE_STEP = 1

# Number that big enough to be ensured that iteration will continue
# to the last item in sequence.
LAST_RANGE_ITEM = 100_000

BASE_LIMIT = 40  # Limit of items per page

BASE_RETRIES = 3

PAGE_ALLOWED_ERRORS = [
    "snackbar__anonymous-recommendations-limit-reached",
    "snackbar__account_offset-forbidden"
]

DEFAULT_TOKEN_TYPE = "Bearer"
