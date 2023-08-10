# The authorization process

Authorization on [Sankaku Complex](https://beta.sankakucomplex.com) can be
performed in two ways:

- via access token
- via credentials (login and password)

### Note

> It is **not** necessary to login into Sankaku Complex at all. You are free
> to send requests to server as unauthorized user, but in that case some methods
> will be unavailable to you (e.g. `get_favorited_posts()`, `get_favorited_books()` etc.).

## Authorization via access token

The following code block shows how to login into account using access token:

```python linenums="1"
import asyncio
import os
from sankaku import SankakuClient

async def main():
    client = SankakuClient()
    await client.login(access_token=os.getenv("ACCESS_TOKEN"))
    # We're using virtual environment variables to prevent
    # private data from accidentally leaking.
    
    # ... Continue to work with API

asyncio.run(main())
```

## Authorization via credentials

Authorization method by credentials is the same as in previous example,
but now user should pass two arguments to `login()` method:

```python linenums="1"
import asyncio
import os
from sankaku import SankakuClient

async def main():
    client = SankakuClient()
    await client.login(
        login=os.getenv("LOGIN"), password=os.getenv("PASSWORD")
    )

    # ... Continue to work with API

asyncio.run(main())
```

## Results

If authorization was successful, server will return response with serialized
json data which will be processed by pydantic. After that user profile model
will be passed to `client.profile` and all further requests to Sankaku servers
will be performed on behalf of logged-in user.
