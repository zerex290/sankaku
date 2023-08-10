# Welcome to sankaku documentation

It is an unofficial API wrapper for [Sankaku Complex](https://beta.sankakucomplex.com)
with *type-hinting*, pydantic *data validation* and an optional *logging support*
with loguru.

<!-- markdownlint-disable-next-line -->
### Features

- Type-hints
- Deserialization of raw json data thanks to pydantic models
- Enumerations for API request parameters to provide better user experience

## Requirements

- Python 3.8+
- aiohttp
- pydantic
- loguru
- aiohttp-retry
- typing_extensions; python_version < '3.10'

## Installation

### Installation with pip

To install sankaku via pip write following line of code in your terminal:

```commandline
pip install sankaku
```

### Installation with Docker

To install the sankaku via Docker, you can follow these steps:

#### Step 1: Install Docker

Ensure that Docker is installed on your machine. If Docker is not already
installed, you can download and install it from the official
[Docker website](https://www.docker.com/get-started).

#### Step 2: Use docker to install sankaku

Open a command prompt. Navigate to the directory where you want
to install sankaku. Type the following command:

```commandline
git clone https://github.com/zerex290/sankaku.git
cd sankaku
docker run -it --name sankaku -w /opt -v$(pwd):/opt python:3 bash
```

## Usage example

```py linenums="1"
import asyncio
from sankaku import SankakuClient

async def main():
    client = SankakuClient()

    post = await client.get_post(25742064)
    print(f"Rating: {post.rating} | Created: {post.created_at}")
    # "Rating: Rating.QUESTIONABLE | Created: 2021-08-01 23:18:52+03:00"

    await client.login(access_token="token")
    # Or you can authorize by credentials:
    # await client.login(login="nickname or email", password="password")

    # Get the first 100 posts which have been added to favorites of the
    # currently logged-in user:
    async for post in client.get_favorited_posts(100):
        print(post)

    # Get every 3rd book from book pages, starting with 100th and ending with
    # 400th book:
    async for book in client.browse_books(100, 401, 3):  # range specified in
        print(book)                                      # same way as with 'range()'

asyncio.run(main())
```
