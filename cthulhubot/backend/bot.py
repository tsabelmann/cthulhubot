"""
"""

from disnake.ext import commands
from disnake.ext.commands import Bot
import disnake


class CthulhuBot(Bot):
    def __init__(self):
        command_sync_flags = commands.CommandSyncFlags.all()
        command_sync_flags.sync_commands = True

        super().__init__(
            command_prefix=["#", "/"],
            help_command=None,
            intents=disnake.Intents.default(),
            command_sync_flags=command_sync_flags,
            activity=disnake.Activity(name="Call of Cthulhu", type=disnake.ActivityType.playing)
        )

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # async def on_message(self, message):
    #     print(f'Message from {message.author}: {message.content}')
