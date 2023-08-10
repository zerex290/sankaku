# About BookClient

BookClient resembles PostClient in terms of functionality. It's because posts
and books are strongly related.

## Browsing books with BookClient

The following code shows how to browse pages with books:

```python linenums="1"
import asyncio
from sankaku.clients import BookClient
from sankaku import types
from sankaku.constants import LAST_RANGE_ITEM

async def main():
    client = BookClient()
    async for book in client.browse_books(
        LAST_RANGE_ITEM,
        favorited_by="Nigredo",
        order=types.BookOrder.POPULARITY
    ):
        print(book.name, book.description)

asyncio.run(main())
```

In the example above we used method `browse_books()` to get all books favorited
by one specific user ('Nigredo' in our case). Predefined constant `LAST_RANGE_ITEM`
is just an integer number high enough to be ensured that we will reach end of
iteration.

## Getting books related to specific post

If specific post id has some books as its parents, you can use
`get_related_books()` method to get such books:

```python linenums="1"
import asyncio
from sankaku.clients import BookClient
from sankaku.constants import LAST_RANGE_ITEM

async def main():
    client = BookClient()
    post_id: int = ...
    related_books = []
    async for book in client.get_related_books(LAST_RANGE_ITEM, post_id=post_id):
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
