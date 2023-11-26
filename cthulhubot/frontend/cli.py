"""
"""

import os

from cthulhubot.backend.bot import CthulhuBot
from cthulhubot.backend.cogs import LegacyCog, Dice, ProbeCog
from dotenv import load_dotenv

from disnake.ext.commands import Bot
from disnake.ext import commands


def main():
    bot = CthulhuBot()
    bot.i18n.load("locale/")

    bot.add_cog(LegacyCog(bot,
                          success_sound_paths=["sounds/success.m4a"],
                          failure_sound_paths=["sounds/fail.m4a"],
                          play_sounds=True)
    )
    bot.add_cog(Dice(bot))
    bot.add_cog(ProbeCog(bot,
                         success_sound_paths=["sounds/success.m4a"],
                         failure_sound_paths=["sounds/fail.m4a"],
                         play_sounds=True)
    )

    # Load environment variables from .env file
    load_dotenv()

    # Get token from environment
    token = os.getenv("DISCORD_TOKEN")

    print(bot.commands)

    bot.run(token)
