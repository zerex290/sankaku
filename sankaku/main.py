from sankaku.client import SankakuClient


async def main() -> None:
    client = await SankakuClient().login("", "")
    print(client.profile.name, client.profile.email)
