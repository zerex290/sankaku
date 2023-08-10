# About TagClient

Tag client has methods for browsing pages with tags and for fetching specific tag.

## Browsing tags with TagClient

Unlike AI-generated posts, whose browsing is restricted and can't be parametrized,
method `browse_tags()` can be parametrized in same way as on website:

```python linenums="1"
import asyncio
from sankaku.clients import TagClient
from sankaku import types

async def main():
    client = TagClient()
    async for tag in client.browse_tags(
        30,  # Specify amount of tags to fetch from server
        order=types.TagOrder.QUALITY,
        sort_parameter=types.SortParameter.POST_COUNT,
        sort_direction=types.SortDirection.DESC
    ):
        print(tag.name, tag.rating, tag.type)

asyncio.run(main())
```

## Getting specific tag

Unlike posts, AI-generated posts or books, specific tag can be returned by its
name or id:

```python linenums="1"
import asyncio
from sankaku.clients import TagClient

async def main():
    client = TagClient()
    tag_id: int = 100
    tag_name: str = "mirco_cabbia"
    tag_by_id = await client.get_tag(tag_id)
    tag_by_name = await client.get_tag(tag_name)

    print(tag_by_id)
    print(tag_by_name)

asyncio.run(main())
```
