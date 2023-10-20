"""Cog that automatically manages voice channels."""
import discord
from discord.ext import commands

from bot.auto_voice_ok.creation import create_new_channel


class AutoVoice(commands.Cog):
    channel_id: int

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.channel_id = 1165049656644993024

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:

        # check if the voice channel joined is the automatic voice channel
        try:
            joined_automatic_voice_channel = after.channel.id == self.channel_id

            if joined_automatic_voice_channel:
                await create_new_channel(member)

        except AttributeError:
            pass


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AutoVoice(bot))
