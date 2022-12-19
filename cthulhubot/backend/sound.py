"""
"""

from pathlib import Path
from disnake import ApplicationCommandInteraction
from disnake import FFmpegPCMAudio
from disnake import Member


async def play_sound(ctx: ApplicationCommandInteraction, file_path: Path):
    # Grab the user who sent the command
    author = ctx.author
    if isinstance(author, Member) \
            and hasattr(author, 'voice') \
            and author.voice is not None \
            and author.voice.channel is not None:
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
