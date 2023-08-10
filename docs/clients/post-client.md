# About PostClient

Client for post browsing has several times more methods than other clients.
That applies to `browse_posts()` method too.

## Browsing posts with post client

Here simple code snippet with post browsing:

```python linenums="1"
import asyncio
from datetime import datetime
from sankaku.clients import PostClient
from sankaku import types

async def main():
    client = PostClient()

    async for post in client.browse_posts(
        100,
        order=types.PostOrder.QUALITY,
        date=[datetime(2020, 1, 12), datetime(2022, 1, 12)],
        tags=["animated"],
        file_type=types.FileType.VIDEO,
        rating=types.Rating.SAFE
    ):
        print(post.file_url)

asyncio.run(main())
```

In the example above we specified:

- amount of posts that we want to fetch;
- rule which will be used to sort posts before fetching;
- date range of posts;
- tags by which posts will be filtered;
- type of posts (e.g. gif, images or video);
- content rating of posts (safe, questionable or explicit (nsfw)).

## Getting specific post by its ID

You can get specific post by its ID like that:

```python linenums="1"
import asyncio
from sankaku.clients import PostClient

async def main():
    post_id: int = 25742064  # Here the ID of the post you interested in
    client = PostClient()
    post = await client.get_post(post_id)
    print(post.file_url)

asyncio.run(main())
```

## About the remaining methods

Almost all the remaining methods inside their definitions invoke method `browse_posts()`
with certain arguments so there is no need to thoroughly consider them.
But it's worth mentioning that methods `get_recommended_posts()` and
`get_favorited_posts()` require authorization.
