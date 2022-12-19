"""
"""
import random

from cthulhubot.backend.cthulhu.probe import Probe
from cthulhubot.backend.sound import play_sound

from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Localized

from pathlib import Path
import typing


class ProbeCog(commands.Cog):
    def __init__(self,
                 bot,
                 success_sound_paths: typing.Union[typing.List[Path], None] = None,
                 failure_sound_paths: typing.Union[typing.List[Path], None] = None,
                 play_sounds: bool = False):
        super().__init__()
        self.bot = bot
        self._success_sound_paths = success_sound_paths
        self._failure_sound_paths = failure_sound_paths
        self._play_sounds = play_sound

    @commands.slash_command(name="probe",
                            description=Localized[str]("Command that allows to probe an investigators ability.",
                                                       key="COMMAND_PROBE_DESCRIPTION"))
    async def probe(self,
                    ctx: ApplicationCommandInteraction,
                    ability: int = commands.Param(
                        name=Localized[str]("ability", key="COMMAND_PROBE_PARAM_ABILITY"),
                        description=Localized[str]("The ability level, usually between 0 and 100",
                                                   key="COMMAND_PROBE_PARAM_ABILITY_DESCRIPTION"),
                        ge=0
                    ),
                    bonus: int = commands.Param(
                        name=Localized[str]("bonus", key="COMMAND_PROBE_PARAM_BONUS"),
                        description=Localized[str]("The number of bonus dice.",
                                                   key="COMMAND_PROBE_PARAM_BONUS_DESCRIPTION"),
                        ge=0,
                        default=0
                    ),
                    malus: int = commands.Param(
                        name=Localized[str]("malus", key="COMMAND_PROBE_PARAM_MALUS"),
                        description=Localized[str]("The number of malus dice.",
                                                   key="COMMAND_PROBE_PARAM_MALUS_DESCRIPTION"),
                        ge=0,
                        default=0
                    )
                    ):
        try:
            probe = Probe(ability, bonus, malus)
            probe_result = probe.probe()

            user_name = ctx.user.display_name
            result = probe_result.render(user_name)
            await ctx.response.send_message(result)

            if self._play_sounds:
                if probe_result.value() == 1 and self._success_sound_paths is not None:
                    path = random.choice(self._success_sound_paths)
                    await play_sound(ctx, path)

                elif probe_result.value() == 100 and self._failure_sound_paths is not None:
                    path = random.choice(self._failure_sound_paths)
                    await play_sound(ctx, path)

        except ValueError:
            await ctx.response.send_message("Either the **bonus** or **malus** parameter is allowed to be greater "
                                            "zero, not both.")
