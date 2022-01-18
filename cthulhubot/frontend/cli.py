"""
"""

import os

from cthulhubot import client
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get token from environment
    token = os.getenv("DISCORD_TOKEN")

    client.run(token)
