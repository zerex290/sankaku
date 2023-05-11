HEADERS: dict[str, str] = {
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
POST_URL = f"{API_URL}/posts"
AI_POST_URL = f"{API_URL}/ai_posts"
TAG_URL = f"{API_URL}/tags"
USER_URL = f"{API_URL}/users"

# Not fully completed urls for usage with str.format()
TAG_WIKI_URL = f"{API_URL}/tag-and-wiki/{{ref}}/{{name_or_id}}"
COMMENT_URL = f"{API_URL}/posts/{{post_id}}/comments"

BASE_RPS = 3
BASE_RPM = 180
BASE_PAGE_NUMBER = 1
BASE_PAGE_LIMIT = 40
