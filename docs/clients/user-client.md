# About UserClient

Methods of UserClient enables you browse pages with users or get specific user.

## Browsing users with UserClient

User browsing can be parametrized by specifying Order rule or level of users:

```python linenums="1"
import asyncio
from datetime import datetime
from sankaku.clients import UserClient
from sankaku import types

async def main():
    client = UserClient()
    async for user in client.browse_users(
        1000,
        order=types.UserOrder.OLDEST,
        level=types.UserLevel.CONTRIBUTOR
    ):
        print(user.created_at < datetime(2020, 12, 18).astimezone())

asyncio.run(main())
```

## Getting specific user

By analogy with `get_tag()` method you can get information about specific user
by its nickname or id:

```python linenums="1"
import asyncio
from sankaku.clients import UserClient

async def main():
    client = UserClient()
    user_id: int = 3242
    user_name: str = "reichan"
    user_by_id = await client.get_user(user_id)
    user_by_name = await client.get_user(user_name)

    print(user_by_id)
    print(user_by_name)

asyncio.run(main())
```
