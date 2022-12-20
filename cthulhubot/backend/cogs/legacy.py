"""
"""

from cthulhubot.backend.cthulhu.probe import Probe
from cthulhubot.backend.sound import play_sound

from disnake.ext import commands
from pathlib import Path

import random
import typing


class LegacyCog(commands.Cog):
    def __init__(self,
                 bot,
                 success_sound_paths: typing.Union[typing.List[Path], None] = None,
                 failure_sound_paths: typing.Union[typing.List[Path], None] = None,
                 play_sounds: bool = False):
        super().__init__()
        self.bot = bot
        self._success_sound_paths = success_sound_paths
        self._failure_sound_paths = failure_sound_paths
        self._play_sounds = play_sounds

    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context):
        await ctx.send(f"arg=")

    @commands.command(name="probe")
    async def probe(self, ctx: commands.Context, *args: str):
        content = ' '.join(args)

        try:
            probe = Probe.from_str(content)
            probe_result = probe.probe()

            user_name = ctx.author.display_name
            result = probe_result.render(user_name)
            await ctx.send(result)

            if self._play_sounds:
                if probe_result.value() == 1 and self._success_sound_paths is not None:
                    path = random.choice(self._success_sound_paths)
                    await play_sound(ctx, path)

                elif probe_result.value() == 100 and self._failure_sound_paths is not None:
                    path = random.choice(self._failure_sound_paths)
                    await play_sound(ctx, path)
        except ValueError:
            await ctx.send("Either the **bonus** or **malus** parameter is allowed to be greater "
                           "zero, not both.")
