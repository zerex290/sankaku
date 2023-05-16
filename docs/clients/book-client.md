---
title: About BookClient
---

BookClient resembles PostClient in terms of functionality. It's because posts
and books are strongly related.

## Browsing books with BookClient

The following code shows how to browse pages with books:

```python
import asyncio
from sankaku.clients import BookClient
from sankaku import types

async def main():
    client = BookClient()
    async for book in client.browse_books(
        favorited_by="Nigredo", order=types.BookOrder.POPULARITY
    ):
        print(book.name, book.description)
        # ... Continue fetching books or break

asyncio.run(main())
```

## Getting books related to specific post

If specific post id has some books as its parents, you can use
`get_related_books()` method to get such books:

```python
import asyncio
from sankaku.clients import BookClient

async def main():
    client = BookClient()
    post_id: int = ...
    related_books = []
    async for book in client.get_related_books(post_id):
        related_books.append(book)

asyncio.run(main())
```

## Getting specific book by its ID

If you know specific book ID then you can get remaining parameters. Peculiarity of
that method is that it returns the whole book information (including another
posts that are part of book):

```python
import asyncio
from sankaku.clients import BookClient

async def main():
    client = BookClient()
    book_id: int = 14562
    book = await client.get_book(book_id)
    print("\n".join(post.file_url for post in book.posts))

asyncio.run(main())
```

## About the remaining methods

All the remaining methods inside their definitions invoke method `browse_books()`
with certain arguments so there is no need to thoroughly consider them. Also,
all the remaining mehtods require authentication.