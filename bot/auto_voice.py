"""Cog that automatically manages voice channels."""
import discord
from discord.ext import commands

from bot.auto_voice_ok.creation import create_new_channel


class AutoVoice(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.channel_id = 1165049656644993024
        self.channel_list = []

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:

        # check if the voice channel joined is the automatic voice channel
        try:
            joined_automatic_voice_channel = after.channel.id == self.channel_id

            if joined_automatic_voice_channel:
                new_channel = await create_new_channel(member, after.channel.category)
                self.channel_list.append(new_channel)

        except AttributeError:
            pass

        # check if the channel the member left was automatically created
        # and if the channel doesn't have any members connected, delete it
        all_left_automatic_voice_channel = before.channel in self.channel_list
        if all_left_automatic_voice_channel and not before.channel.members:
            await before.channel.delete()


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AutoVoice(bot))
