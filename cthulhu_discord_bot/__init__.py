"""Module that provides the connection, the commands, and the utility functions for bonus, malus, and messages."""

# Import A
import asyncio

# Import D
import discord
from discord.ext import commands

# Import D
from dotenv import load_dotenv

# Import O
import os

# Import P
import pathlib

# Import R
import re
import random

# PATH

# Path to this directory
__dir__path__ = pathlib.Path(__file__).parent.parent

__dice_success_path__ = __dir__path__.joinpath(pathlib.Path("sound/success.m4a")).resolve()

__dice_fail_path__ = __dir__path__.joinpath(pathlib.Path("sound/fail.m4a")).resolve()

# ENV

# Load environment variables from .env file
load_dotenv()

# Create client
client = commands.Bot(command_prefix="#")

# Get token from environment
token = os.getenv("DISCORD_TOKEN")

__dice_regex__ = re.compile(
    r'(?P<dice>(\s*\+?\s*[0-9]{1,2}([dD])[0-9]+)+)\s*(?P<values>(\s*([+\-])\s*[0-9]{1,2})*\s*)'
)

__die_regex__ = re.compile(
    r"\s*(?P<dice>[0-9]{1,2})([dD])(?P<value>[0-9]+)\s*"
)

__calculus_regex__ = re.compile(
    r'\s*((?P<sign>([+\-]))\s*(?P<value>[0-9]{1,2}))\s*'
)

__probe_regex__ = re.compile(
    r'\s*(?P<probe>[0-9]{1,2})(\s+(?P<id>m|M|b|B|bon|mal|bonus|malus)\s+(?P<value>[0-9]{1,2}))?\s*'
)

__bonus_malus_regex__ = re.compile(
    r'\s*(?P<value>([0-9]+))\s*'
)


# Probe Message Computation
def probe_message(probe_value: int, die_value: int):
    if die_value == 1:
        return "Critical success"
    elif die_value <= (probe_value // 5):
        return "Extreme success"
    elif die_value <= (probe_value // 2):
        return "Difficult success"
    elif die_value <= probe_value:
        return "Regular success"
    else:
        if probe_value < 50:
            if die_value >= 96:
                return "You are doomed!"
            else:
                return "You have screwed up!"
        else:
            if die_value == 100:
                return "You are doomed!"
            else:
                return "You have screwed up!"


# Compute bonus
def compute_bonus(die_10: int, die_1: int, bonus_dice: int = 0):
    # Throw bonus_dice amount of bonus d10 dice
    dice = [random.randint(0, 9) * 10 for _ in range(bonus_dice)]

    # Compute dice value
    die_value = dice2value(die_10, die_1)

    # Decide if bonus is applicable
    if 0 <= die_value <= 10:
        return die_10, dice, False
    else:
        new_dice = [die_10, *dice]
        if 0 in new_dice and die_1 == 0:
            new_dice = [die for die in new_dice if die != 0]

        # Compute new 10 part
        new_die_10 = min(new_dice)

        if new_die_10 == die_10:
            return die_10, dice, False
        else:
            return new_die_10, dice, True


# Compute malus
def compute_malus(die_10: int, die_1: int, malus_dice: int = 0):
    # Throw malus_dice amount of malus d10 dice
    dice = [random.randint(0, 9) * 10 for _ in range(malus_dice)]

    # Decide based on die_1 if 100 can be created
    if die_1 == 0:
        if 0 in dice:
            new_die_10 = 0
        else:
            new_die_10 = max([die_10, *dice])
    else:
        new_die_10 = max([die_10, *dice])

    if new_die_10 == die_10:
        return die_10, dice, False
    else:
        return new_die_10, dice, True


def dice2value(die_10: int, die_1: int):
    if die_10 == 0 and die_1 == 0:
        return 100
    else:
        return die_10 + die_1


def value2dice(value):
    if value == 100:
        return 0, 0
    else:
        die_10 = (value // 10) * 10
        die_1 = value % 10
        return die_10, die_1


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(name="Awaken me..."), )
    print("I am online")


@client.command(name="roll")
async def roll(ctx):
    message = ctx.message.content
    match = __dice_regex__.search(message)

    if match:
        rng_numbers = []
        for m in __die_regex__.finditer(match.group("dice")):
            dice = m.group("dice")
            dice = int(dice)

            value = m.group("value")
            value = int(value)

            rng_numbers.append([random.randint(1, value) for _ in range(dice)])

        rng_sum = sum([sum(rng) for rng in rng_numbers])

        # Change sum
        additions = []
        for m in __calculus_regex__.finditer(match.group("values")):
            group = m.groupdict()
            sign = group["sign"]

            calc_value = group["value"]
            calc_value = int(calc_value)

            if sign == "+":
                additions.append(+calc_value)

            elif sign == "-":
                additions.append(+calc_value)

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


@client.command(name="probe")
async def probe(ctx):
    message = ctx.message.content
    match = __probe_regex__.search(message)

    if match:
        # Compute transmitted probe (ability) value
        probe_value = match.group("probe")
        probe_value = int(probe_value)

        # Throw 1d10 as tens unit
        die_10 = random.randint(0, 9) * 10

        # Throw 1d10
        die_1 = random.randint(0, 9)

        # Get author name, preferable nickname, secondly normal user name
        author_name = ctx.message.author.nick or ctx.message.author.name

        # Bonus / Malus computation
        if match.group("id") and match.group("id").lower() in ["b", "B", "bon", "bonus"]:
            # Get amount of bonus dice
            bonus_dice = match.group("value")
            bonus_dice = int(bonus_dice)

            # Compute bonus
            new_die_10, dice, applied = compute_bonus(die_10, die_1, bonus_dice)

            # Compute die_value
            die_value = dice2value(new_die_10, die_1)

            # Probe message
            probe_mess = probe_message(probe_value, die_value)

            if applied:
                # Compute index in dice that holds the die_10 value
                index = dice.index(new_die_10)

                # Compute new dice string
                lst = [f"**{die:02d}**" if i == index else f"{die:02d}" for i, die in enumerate(dice)]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(f"""**{author_name}**\n"""
                               f"""Roll: [{die_10:02d}][**{die_1}**] Ability: **{probe_value}**\n"""
                               f"""Bonus: {dice_str}\n"""
                               f"""Result: **{die_value}**\n"""
                               f"""**{probe_mess}**""")
            else:
                # Compute new dice string
                lst = [f"{die:02d}" for die in dice]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(f"""**{author_name}**\n"""
                               f"""Roll: [**{die_10:02d}**][**{die_1}**] Ability: **{probe_value}**\n"""
                               f"""Bonus: {dice_str}\n"""
                               f"""Result: **{die_value}**\n"""
                               f"""**{probe_mess}**""")

            # Play sound
            if die_value == 1:
                await play_sound(ctx, __dice_success_path__)
            elif die_value == 100:
                await play_sound(ctx, __dice_fail_path__)

        elif match.group("id") and match.group("id").lower() in ["m", "M", "mal", "malus"]:
            # Get amount of bonus dice
            malus_dice = match.group("value")
            malus_dice = int(malus_dice)

            # Compute malus
            new_die_10, dice, applied = compute_malus(die_10, die_1, malus_dice)

            # Compute die_value
            die_value = dice2value(new_die_10, die_1)

            # Probe message
            probe_mess = probe_message(probe_value, die_value)

            if applied:
                # Compute index in dice that holds the die_10 value
                index = dice.index(new_die_10)

                # Compute new dice string
                lst = [f"**{die:02d}**" if i == index else f"{die:02d}" for i, die in enumerate(dice)]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(f"""**{author_name}**\n"""
                               f"""Roll: [{die_10:02d}][**{die_1}**] Ability: **{probe_value}**\n"""
                               f"""Malus: {dice_str}\n"""
                               f"""Result: **{die_value}**\n"""
                               f"""**{probe_mess}**""")
            else:
                # Compute new dice string
                lst = [f"{die:02d}" for die in dice]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(f"""**{author_name}**\n"""""
                               f"""Roll: [**{die_10:02d}**][**{die_1}**]  Ability: **{probe_value}**\n"""
                               f"""Malus: {dice_str}\n"""
                               f"""Result: **{die_value}**\n"""
                               f"""**{probe_mess}**""")

            # Play sound
            if die_value == 1:
                await play_sound(ctx, __dice_success_path__)
            elif die_value == 100:
                await play_sound(ctx, __dice_fail_path__)

        else:
            # Compute die value
            die_value = dice2value(die_10, die_1)

            # Probe message
            probe_mess = probe_message(probe_value, die_value)

            # Print message
            await ctx.send(f"""**{author_name}**\n"""
                           f"""Roll: [**{die_10:02d}**][**{die_1}**] Ability: **{probe_value}**\n"""
                           f"""Result: **{die_value}**\n"""
                           f"""**{probe_mess}**""")

            # Play sound
            if die_value == 1:
                await play_sound(ctx, __dice_success_path__)
            elif die_value == 100:
                await play_sound(ctx, __dice_fail_path__)

    else:
        return


async def play_sound(ctx, file_path):
    # grab the user who sent the command
    user = ctx.message.author
    voice_channel = user.voice.channel
    channel = None
    if voice_channel is not None:
        voice_channel = ctx.author.voice.channel
        voice = ctx.channel.guild.voice_client
        if voice is None:
            voice = await voice_channel.connect()
        elif voice.channel != voice_channel:
            await voice.move_to(voice_channel)
        voice.play(discord.FFmpegPCMAudio(file_path))
    else:
        pass
        #await client.say('User is not in a channel.')


def main():
    client.run(token)


if __name__ == "__main__":
    main()
