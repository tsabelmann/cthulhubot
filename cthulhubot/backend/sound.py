"""
"""

from pathlib import Path
from disnake import Interaction
from disnake.ext.commands import Context
from disnake import FFmpegPCMAudio
from disnake import Member
import typing


async def play_sound(ctx: typing.Union[Interaction, Member], file_path: Path):
    if (isinstance(ctx, Member)):
        author = ctx
        
        # Grab the user who sent the command
        if hasattr(author, 'voice') and (author.voice is not None) and (author.voice.channel is not None):
            # Get voice channel the author is in
            voice_channel = author.voice.channel

            # Get the (output) voice of the bot
            voice = ctx.guild.voice_client
            if voice is None:
                # Join voice channel of the author and get the (output) voice
                voice = await voice_channel.connect()
            elif voice.channel != voice_channel:
                # Change (output) voice of bot if it is on a different channel
                await voice.move_to(voice_channel)

            # Play audio
            voice.play(FFmpegPCMAudio(file_path))
        else:
            pass
    elif (isinstance(ctx, Interaction)):
        author = ctx.author
        
        # Grab the user who sent the command
        if hasattr(author, 'voice') and (author.voice is not None) and (author.voice.channel is not None):
            # Get voice channel the author is in
            voice_channel = ctx.author.voice.channel

            # Get the (output) voice of the bot
            voice = ctx.channel.guild.voice_client
            if voice is None:
                # Join voice channel of the author and get the (output) voice
                voice = await voice_channel.connect()
            elif voice.channel != voice_channel:
                # Change (output) voice of bot if it is on a different channel
                await voice.move_to(voice_channel)

            # Play audio
            voice.play(FFmpegPCMAudio(file_path))
        else:
            pass
    else:
        # print("I am here!")
        # print(type(ctx))
        return
        
    # # Grab the user who sent the command
    # if hasattr(author, 'voice') and (author.voice is not None) and (author.voice.channel is not None):
    #     # Get voice channel the author is in
    #     voice_channel = ctx.author.voice.channel

    #     # Get the (output) voice of the bot
    #     voice = ctx.channel.guild.voice_client
    #     if voice is None:
    #         # Join voice channel of the author and get the (output) voice
    #         voice = await voice_channel.connect()
    #     elif voice.channel != voice_channel:
    #         # Change (output) voice of bot if it is on a different channel
    #         await voice.move_to(voice_channel)

    #     # Play audio
    #     voice.play(FFmpegPCMAudio(file_path))
    # else:
    #     pass
