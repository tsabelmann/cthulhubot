# Import D
import discord
from discord.ext import commands

# Import D
from dotenv import load_dotenv

# Import O
import os

# Import R
import re
import random

# Load environment variables from .env file
load_dotenv()

# Create client
client = commands.Bot(command_prefix="#")

# Get token from environment
token = os.getenv("DISCORD_TOKEN")

__dice_regex__ = re.compile(
    r'(?P<dice>(\s*\+?\s*[0-9]{1,2}(d|D)[0-9]+)+)\s*(?P<values>(\s*(\+|-)\s*[0-9]{1,2})*\s*)'
)

__die_regex__ = re.compile(
    r"\s*(?P<dice>[0-9]{1,2})(d|D)(?P<value>[0-9]+)\s*"
)

__calculus_regex__ = re.compile(
    r'\s*((?P<sign>(\+|-))\s*(?P<value>[0-9]{1,2}))\s*'
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
def compute_bonus(die_value: int, bonus_dice: int = 0):
    dice = [random.randint(0, 10) * 10 for _ in range(bonus_dice)]
    if 0 <= die_value <= 10:
        return die_value, dice, False
    else:
        # Compute 10 part
        die_10 = (die_value // 10) * 10

        # Compute 1 part
        die_1 = die_value % 10

        # Compute new 10 part
        new_die_10 = min([die_10, *dice])

        if new_die_10 == die_10:
            return die_value, die_10, dice, False
        else:
            # Compute new die value
            new_die_value = new_die_10 + die_1

            return new_die_value, new_die_10, dice, True


# Compute malus
def compute_malus(die_value: int, malus_dice: int = 0):
    # Malus Dice
    dice = [random.randint(0, 10) * 10 for _ in range(malus_dice)]

    # Compute 10 part
    die_10 = (die_value // 10) * 10

    # Compute 1 part
    die_1 = die_value % 10

    new_dice = []
    if die_1 != 0:
        if 100 in dice:
            new_dice = filter(lambda x: x != 100, [die_10, *dice])
        else:
            new_dice = dice
    else:
        new_dice = dice

    # Compute new 10 part
    new_die_10 = max([die_10, *new_dice])

    if new_die_10 == die_10:
        return die_value, die_10, dice, False
    else:
        # Compute new die value
        new_die_value = new_die_10 + die_1

        return new_die_value, new_die_10, dice, True


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game("Awaken me..."))
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

            rng_numbers.append([random.randint(1, value) for i in range(dice)])

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


@client.command(name="bonus")
async def bonus(ctx, bonus_dice=1):
    # Random Die Value from [1,100]
    die_roll = random.randint(1, 100)

    # Compute bonus
    die_value, die_10, dice, applied = compute_bonus(die_roll, bonus_dice)

    # Get author name, preferable nickname, secondly normal user name
    author_name = ctx.message.author.nick or ctx.message.author.name

    if applied:
        # Compute index in dice that holds the die_10 value
        index = dice.index(die_10)

        # Compute new dice string
        lst = [f"**{die}**" if i == index else f"{die}" for i, die in enumerate(dice)]
        dice_str = f"[{', '.join(lst)}]"

        await ctx.send(f"**{author_name}**\nRoll: **{die_roll}**\nBonus: {dice_str}\nResult: **{die_value}**")
    else:
        await ctx.send(f"**{author_name}**\nRoll: **{die_roll}**\nBonus: {dice}\nResult: **{die_value}**")


@client.command(name="malus")
async def malus(ctx, malus_dice=1):
    # Random Die Value from [1,100]
    die_roll = random.randint(1, 100)

    # Compute malus
    die_value, die_10, dice, applied = compute_malus(die_roll, malus_dice)

    # Get author name, preferable nickname, secondly normal user name
    author_name = ctx.message.author.nick or ctx.message.author.name

    if applied:
        # Compute index in dice that holds the die_10 value
        index = dice.index(die_10)

        # Compute new dice string
        lst = [f"**{die}**" if i == index else f"{die}" for i, die in enumerate(dice)]
        dice_str = f"[{', '.join(lst)}]"

        await ctx.send(f"**{author_name}**\nRoll: **{die_roll}**\nMalus: {dice_str}\nResult: **{die_value}**")
    else:
        await ctx.send(f"**{author_name}**\nRoll: **{die_roll}**\nMalus: {dice}\nResult: **{die_value}**")


@client.command(name="probe")
async def probe(ctx):
    message = ctx.message.content
    match = __probe_regex__.search(message)

    if match:
        # Compute transmitted probe (ability) value
        probe_value = match.group("probe")
        probe_value = int(probe_value)

        # Throw 1d100
        die_roll = random.randint(1, 100)

        # Get author name, preferable nickname, secondly normal user name
        author_name = ctx.message.author.nick or ctx.message.author.name

        # Bonus / Malus computation
        if match.group("id") and match.group("id").lower() in ["b", "B", "bon", "bonus"]:
            # Get amount of bonus dice
            bonus_dice = match.group("value")
            bonus_dice = int(bonus_dice)

            # Compute bonus
            die_value, die_10, dice, applied = compute_bonus(die_roll, bonus_dice)

            # Probe message
            probe_mess = probe_message(probe_value, die_value)

            if applied:
                # Compute index in dice that holds the die_10 value
                index = dice.index(die_10)

                # Compute new dice string
                lst = [f"**{die}**" if i == index else f"{die}" for i, die in enumerate(dice)]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(
                    f"**{author_name}**\nRoll: **{die_roll}** Ability: **{probe_value}**\nMalus: {dice_str}\nResult: **{die_value}**\n**{probe_mess}**")
            else:
                # Print message
                await ctx.send(
                    f"**{author_name}**\nRoll: **{die_roll}** Ability: **{probe_value}**\nMalus: {dice}\nResult: **{die_value}**\n**{probe_mess}**")

        elif match.group("id") and match.group("id").lower() in ["m", "M", "mal", "malus"]:
            # Get amount of bonus dice
            malus_dice = match.group("value")
            malus_dice = int(malus_dice)

            # Compute malus
            die_value, die_10, dice, applied = compute_malus(die_roll, malus_dice)

            # Probe message
            probe_mess = probe_message(probe_value, die_value)

            if applied:
                # Compute index in dice that holds the die_10 value
                index = dice.index(die_10)

                # Compute new dice string
                lst = [f"**{die}**" if i == index else f"{die}" for i, die in enumerate(dice)]
                dice_str = f"[{', '.join(lst)}]"

                # Print message
                await ctx.send(
                    f"**{author_name}**\nRoll: **{die_roll}** Ability: **{probe_value}**\nMalus: {dice_str}\nResult: **{die_value}**\n**{probe_mess}**")
            else:
                # Print message
                await ctx.send(
                    f"**{author_name}**\nRoll: **{die_roll}** Ability: **{probe_value}**\nMalus: {dice}\nResult: **{die_value}**\n**{probe_mess}**")

        else:
            # Probe message
            probe_mess = probe_message(probe_value, die_roll)

            # Print message
            await ctx.send(f"""**{author_name}**\nRoll: **{die_roll}** Ability: **{probe_value}**\n**{probe_mess}**""")
    else:
        return


if __name__ == "__main__":
    client.run(token)
