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
    r'\s*(?P<probe>[0-100]{1,2})\s+((?P<id>m|M|b|B|bon|mal|bonus|malus)\s+(?P<value>[0-9]{1,2}))?\s*'
)

__bonus_malus_regex__ = re.compile(
    r'\s*(?P<value>([0-9]+))\s*'
)


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

            rng_numbers.extend([random.randint(1, value) for i in range(dice)])

        rng_sum = sum(rng_numbers)

        print(match.group("values"))

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

        rng_sum += sum(additions)

        author_name = ctx.message.author.nick or ctx.message.author.name

        await ctx.send(f"**{author_name}**\nRoll: `{rng_numbers}`\nAdditions: {additions}\nResult: **{rng_sum}**")
    else:
        return


@client.command(name="bonus")
async def bonus(ctx, bonus_dice=1):
    # Random Die Value from [1,100]
    die_value = random.randint(1, 100)

    # Assign the old die value to the return value new_die_value
    new_die_value = die_value

    dice = [random.randint(0, 10)*10 for _ in range(bonus_dice)]
    if 0 <= die_value <= 10:
        pass
    else:
        # Compute 10 part
        die_10 = (die_value // 10) * 10

        # Compute 1 part
        die_1 = die_value % 10

        # Compute new 10 part
        new_die_10 = min([die_10, *dice])

        # Compute new die value
        new_die_value = new_die_10 + die_1

    # Sort die values in ascending order
    dice.sort()

    # Get author name, preferable nickname, secondly normal user name
    author_name = ctx.message.author.nick or ctx.message.author.name

    await ctx.send(f"**{author_name}**\nRoll: `{die_value}`\nBonus: {dice}\nResult: **{new_die_value}**")


@client.command(name="malus")
async def malus(ctx, malus_dice=1):
    # Random Die Value from [1,100]
    die_value = random.randint(1, 100)

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

    # Compute new die value
    new_die_value = new_die_10 + die_1

    # Get author name, preferable nickname, secondly normal user name
    author_name = ctx.message.author.nick or ctx.message.author.name

    await ctx.send(f"**{author_name}**\nRoll: `{die_value}`\nMalus: {dice}\nResult: **{new_die_value}**")


@client.command(name="probe")
async def probe(ctx):
    message = ctx.message.content
    match = __probe_regex__.search(message)

    if match:
        await ctx.send(match.groupdict())


if __name__ == "__main__":
    client.run(token)