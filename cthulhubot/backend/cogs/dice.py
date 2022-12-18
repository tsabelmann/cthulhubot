"""
"""
import random

from disnake.ext import commands
from disnake import ApplicationCommandInteraction, User, Localized

from random import randint
from typing import List


class Dice(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name=Localized("d4", key="COMMAND_D4_NAME"), description=Localized(key="COMMAND_D4_DESCRIPTION"))
    async def d4(self, ctx: ApplicationCommandInteraction):
        value = randint(1, 4)
        await ctx.send(f"Roll: [{value}]")

    @commands.slash_command(name=Localized("d6", key="COMMAND_D6_NAME"), description=Localized(key="COMMAND_D6_DESCRIPTION"))
    async def d6(self, ctx: ApplicationCommandInteraction):
        value = randint(1, 6)
        await ctx.send(f"Roll: [{value}]")

    @commands.slash_command(name=Localized("d8", key="COMMAND_D8_NAME"), description=Localized(key="COMMAND_D8_DESCRIPTION"))
    async def d8(self, ctx: ApplicationCommandInteraction):
        value = randint(1, 8)
        await ctx.send(f"Roll: [{value}]")

    @commands.slash_command(name=Localized("d12", key="COMMAND_D12_NAME"), description=Localized(key="COMMAND_D12_DESCRIPTION"))
    async def d12(self, ctx: ApplicationCommandInteraction):
        value = randint(1, 12)
        await ctx.send(f"Roll: [{value}]")

    @commands.slash_command(name=Localized("d20", key="COMMAND_D20_NAME"), description=Localized(key="COMMAND_D20_DESCRIPTION"))
    async def d20(self, ctx: ApplicationCommandInteraction):
        value = randint(1, 20)
        await ctx.send(f"Roll: [{value}]")
