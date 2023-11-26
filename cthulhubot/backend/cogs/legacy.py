"""
"""

from cthulhubot.backend.cthulhu.probe import Probe
from cthulhubot.backend.sound import play_sound

from disnake.ext import commands
from pathlib import Path

import re
import random
import typing


__dice_regex__ = re.compile(
    r'(\s*[+\-]?\s*[1-9][0-9]*([dDwW][1-9][0-9]*)?)+'
)

__die_regex__ = re.compile(
    r'(?P<sign>[+\-])?\s*(?P<value>[1-9][0-9]*)([dDwW](?P<dvalue>[1-9][0-9]*))?'
)


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

    @commands.command(name="roll", aliases=["r"])
    async def roll(self, ctx: commands.Context):
        message = ctx.message.content
        match = __dice_regex__.search(message)

        if match:
            # List of random dice
            rng_numbers = []

            # List of additions
            additions = []
            for m in __die_regex__.finditer(message):
                # Get sign
                sign = m.group("sign")
                if sign is None or sign == "+":
                    sign = 1
                else:
                    sign = -1

                # Get addition or amount of dice
                value = m.group("value")
                value = int(value)

                # Get die eye value
                dvalue = m.group("dvalue")

                # Decide whether value is additional value or die
                if dvalue is not None:
                    # Compute dvalue (int) from dvalue (str)
                    dvalue = int(dvalue)

                    # Append dice to rng_numbers
                    rng_numbers.append([sign * random.randint(1, dvalue) for _ in range(value)])
                else:
                    # Append additional value
                    additions.append(sign * value)

            # Add random dice to sum
            rng_sum = sum([sum(rng) for rng in rng_numbers])

            # Add additional values to sum
            add_sum = sum(additions)

            # Total sum
            total_sum = rng_sum + add_sum

            # Get author nick name preferably, or, the user name secondly
            author_name = ctx.message.author.nick or ctx.message.author.name

            # Construct message
            await ctx.send(f"""**{author_name}**\n"""
                        f"""Roll: {''.join([str(rng) for rng in rng_numbers])}\n"""
                        f"""Sum: **{rng_sum}**\n"""
                        f"""Additions: {additions}\n"""
                        f"""Sum: **{add_sum}**\n"""
                        f"""Result: **{total_sum}**""")
        else:
            return
        
    
    @commands.command(name="probe", aliases=["p"])
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
