"""Entrypoint for cthulhu discord bot."""

from cthulhu_discord_bot import client, token


if __name__ == "__main__":
    client.run(token)
