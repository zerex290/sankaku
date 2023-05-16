---
title: About AIClient
---

Recently Sankaku Complex developers released feature to generate posts by
usage of neural networks. So AIClient is responsible for managing API requests
to AI-related content.

---

### Disclaimer

> Because AI is feature for premium users, AI client look a bit poor.

---

## Browsing posts with AIClient

For non-premium users there is restriction to directly view posts created by
AI:

![access to AI posts restricted for regular users](assets/restriction.png)

But this restriction can be circumvented by sending requests directly via API.

Here is example of post browsing, using AIClient:

```python
import asyncio
from sankaku.clients import AIClient
from sankaku import types

async def main():
    client = AIClient()
    ai_posts = []

    async for post in client.browse_ai_posts():
        if post.rating is types.Rating.SAFE:  # filter nsfw content
            ai_posts.append(post)
        if len(ai_posts) >= 10:  # for instance, we need to fetch 10 sfw posts
            break
    
    print("\n".join(post.file_url for post in ai_posts if post.file_url is not None))

asyncio.run(main())
```

## Getting specific AI post

If there is situation when you know ID of the post and want to fetch its data
from server, you can do it like this:

```python
import asyncio
from sankaku.clients import AIClient

async def main():
    post_id: int = 23432  # Here the ID of the post you interested in
    client = AIClient()
    post = await client.get_ai_post(post_id)
    print(post.file_url)

asyncio.run(main())
```