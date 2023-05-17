# Welcome to sankaku documentation

It is an unofficial API wrapper for [Sankaku Complex](https://beta.sankakucomplex.com)
with *type-hinting*, pydantic *data validation* and an optional *logging support*
with loguru.

### Features

- Type-hints
- Deserialization of raw json data thanks to pydantic models
- Enumerations for API request parameters to provide better user experience
  > For instance, you can type `types.TagType.ARTIST` instead of `types[]=1`

## Requirements

- Python 3.11+
- aiohttp
- pydantic
- loguru

## Installation

To install sankaku via pip write following line of code in your terminal:

```commandline
pip install sankaku
```

To install the sankaku via Docker, you can follow these steps:

###### Step 1: Install Docker

Ensure that Docker is installed on your machine. If Docker is not already
installed, you can download and install it from the official
[Docker website](https://www.docker.com/get-started).

###### Step 2: Use docker to install sankaku

Open a command prompt. Navigate to the directory where you want
to install Sankaku. Type the following command:

```commandline
git clone https://github.com/zerex290/sankaku.git
cd sankaku
docker run -it --name sankaku -w /opt -v$(pwd):/opt python:3.11 bash
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
    async for book in client.get_recently_read_books():
        ...

asyncio.run(main())
```
