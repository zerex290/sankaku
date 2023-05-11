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
