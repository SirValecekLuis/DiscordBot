"""Cog that automatically manages voice channels."""
import discord
from discord.ext import commands

from bot.auto_voice_ok.creation import create_new_channel


class AutoVoice(commands.Cog):

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.channel_id = -1
        self.channel_list = []

    # clear empty voice channels that were genereted before this session started
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for each in self.channel_list:
            channel = self.bot.get_channel(each)

            # if channel doesnt have any members connected delete it
            if not channel.members:
                await each.channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        # check if a automatic voice channel is set, if not dont do anything
        if self.channel_id == -1:
            return

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

        try:
            is_automatic_voice_channel = before.channel.id in self.channel_list

        except AttributeError:
            is_automatic_voice_channel = False

        if is_automatic_voice_channel and not before.channel.members:
            await before.channel.delete()

    # set the automatic voice channel id to the one specified by the user
    @commands.slash_command(name="setautovoicechannel")
    async def set_auto_voice(self, ctx, auto_channel_id: str) -> None:
        self.channel_id = int(auto_channel_id)
        await ctx.respond("Automatic voice channel set!")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AutoVoice(bot))
