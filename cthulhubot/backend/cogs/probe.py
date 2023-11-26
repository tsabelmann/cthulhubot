"""
"""
import random
from typing import Any, Coroutine, Optional

from disnake.interactions import MessageInteraction

from cthulhubot.backend.cthulhu.probe import Probe
from cthulhubot.backend.sound import play_sound

from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Localized, LocalizationValue
from disnake.ui import Button, View, button
from disnake import ButtonStyle

from pathlib import Path
import typing


class ProbeForceView(View):
    def __init__(self, user, cog, ability: int, bonus: int, malus: int, probe_result, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)
        self.user = user
        self.cog = cog
        self.ability = ability
        self.bonus = bonus
        self.malus = malus
        self.probe_result = probe_result
        self.message = None
        self.updated = False
        
    @button(label="Force?", style=ButtonStyle.red)
    async def on_button_pressed(self, button, interaction):
        
        probe = Probe(self.ability, self.bonus, self.malus)
        probe_result = probe.probe()
        user_name = self.user.display_name
        result = probe_result.render(user_name)
        
        self.updated = True
        await interaction.message.edit(result, view=None)
        
        if self.cog._play_sounds:
            if probe_result.value() == 1 and self.cog._success_sound_paths is not None:
                path = random.choice(self.cog._success_sound_paths)
                await play_sound(interaction, path)

            elif probe_result.value() == 100 and self.cog._failure_sound_paths is not None:
                path = random.choice(self.cog._failure_sound_paths)
                await play_sound(interaction, path)    
        
    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if interaction.user == self.user:
            return True
        else:
            await interaction.response.send_message(f"{interaction.user} you are not allowed to force the throw!", ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        if (self.message != None):
            await self.message.edit(view=None)
            
        if self.updated == False:
            self.updated = True
            if self.cog._play_sounds:
                if self.probe_result.value() == 1 and self.cog._success_sound_paths is not None:
                    path = random.choice(self.cog._success_sound_paths)
                    await play_sound(self.user, path)

                elif self.probe_result.value() == 100 and self.cog._failure_sound_paths is not None:
                    path = random.choice(self.cog._failure_sound_paths)
                    await play_sound(self.user, path) 
            

class ProbeCog(commands.Cog):
    def __init__(self,
                 bot,
                 success_sound_paths: typing.Union[typing.List[Path], None] = None,
                 failure_sound_paths: typing.Union[typing.List[Path], None] = None,
                 play_sounds: bool = False):
        super().__init__()
        self.bot: commands.Bot = bot
        self._success_sound_paths = success_sound_paths
        self._failure_sound_paths = failure_sound_paths
        self._play_sounds = play_sounds

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
                    ),
                    description: str = commands.Param(
                        name=Localized[str]("description", key="COMMAND_PROBE_PARAM_DESCRIPTION"),
                        description=Localized[str]("The ability description.",
                                                   key="COMMAND_PROBE_PARAM_DESCRIPTION_DESCRIPTION"),
                        default=""
                    )
                    ):
        try:
            probe = Probe(ability, bonus, malus)
            probe_result = probe.probe()
            user_name = ctx.user.display_name
            result = probe_result.render(user_name)
            
            if probe_result.is_success():
                await ctx.response.send_message(result)
                
                if self._play_sounds:
                    if probe_result.value() == 1 and self._success_sound_paths is not None:
                        path = random.choice(self._success_sound_paths)
                        await play_sound(ctx, path)

                    elif probe_result.value() == 100 and self._failure_sound_paths is not None:
                        path = random.choice(self._failure_sound_paths)
                        await play_sound(ctx, path)    
            else:
                view = ProbeForceView(ctx.user, self, ability, bonus, malus, probe_result, timeout=10)
                await ctx.response.send_message(result, view=view)
                view.message = await ctx.original_response()
                                                            
        except ValueError:
            await ctx.response.send_message("Either the **bonus** or **malus** parameter is allowed to be greater "
                                            "zero, not both.")