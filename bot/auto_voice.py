"""Cog that automatically manages voice channels."""
import discord
from discord.ext import commands

from start import db
from error_handling import send_error_message_to_user


async def create_new_channel(user: discord.Member, category: discord.CategoryChannel) -> int:
    """
    This creates a new channel after user joins "Obecné" voice channel.
    :param user: User who joined
    :param category: Voice channel category
    :return: ID of created channel as int
    """

    discord_server = user.guild

    # create the voice channel name from username or nickname
    new_channel_name = user.name
    if user.nick is not None:
        new_channel_name = user.nick
    new_channel_name += "'s channel"

    # create the new channel
    created_channel = await discord_server.create_voice_channel(name=new_channel_name, category=category)

    # move the user to the newly created channel
    await user.move_to(created_channel)

    # return the created channel
    return created_channel.id


class AutoVoice(commands.Cog):
    """A Cog that handles voice category, and it automatically gives a person a voice channel when joined."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.channel_id = db.voice_channel_id
        self.channel_list = []

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        When the bot starts, it clears empty voice channels generated before this session started.
        :return:
        """
        # try to get the channel category of the automatic voice channel
        try:
            auto_voice_category = self.bot.get_channel(
                self.channel_id).category

        except AttributeError:
            return

        # get every voice channel in the auto_voice_category
        for channel in auto_voice_category.voice_channels:
            is_auto_voice_master = channel.id == self.channel_id

            # if a channel doesn't have any members connected
            # and if it isn't the auto voice creator itself, delete it
            if not channel.members and not is_auto_voice_master:
                await channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        """
        This function checks if a channel can be deleted after someone leaves.
        :param member: Member, who left
        :param before:
        :param after:
        :return:
        """
        # check if an automatic voice channel is set, if not don't do anything
        if self.channel_id is None:
            return

        # check if the voice channel joined is the automatic voice creator
        try:
            joined_auto_voice_master = after.channel.id == self.channel_id

            if joined_auto_voice_master:
                new_channel = await create_new_channel(member, after.channel.category)
                self.channel_list.append(new_channel)

        except AttributeError:
            pass

        try:
            # get the category of automatic voice channels
            auto_voice_category = self.bot.get_channel(
                self.channel_id).category

            is_automatic_voice_channel = before.channel in auto_voice_category.voice_channels
            is_auto_voice_master = before.channel.id == self.channel_id

            # check if the channel the user left is from the automatic voice category
            # and if it isn't the channel from which the voice channels are created
            can_be_deleted = is_automatic_voice_channel and not is_auto_voice_master

        except AttributeError:
            can_be_deleted = False

        # check if a channel the member left can be deleted
        # and if the channel doesn't have any members connected, delete it
        if can_be_deleted and not before.channel.members:
            await before.channel.delete()

    @commands.slash_command(name="set-auto-voice-channel")
    @commands.has_permissions(administrator=True)
    async def set_auto_voice(self,
                             ctx: discord.ApplicationContext,
                             auto_channel_id: int,
                             storage: discord.Option(
                                 str,
                                 description="Lokálně do proměnné či DB (Databáze preferováno)",
                                 choices=["local", "db"]
                             )) -> None:
        """
        Set the automatic voice primary ID to the one specified by the user.
        :param ctx: Context of slash command
        :param auto_channel_id: ID that should be set as int
        :param storage: Local variable or database
        :return: None
        """

        # check if the id should be stored locally
        if storage == "local":
            self.channel_id = auto_channel_id
            await ctx.respond("Hodnota nastavena do lokální proměnné platné v rámci runtime.", ephemeral=True)
            return

        if storage == "db":
            db.voice_channel_id = auto_channel_id
            self.channel_id = auto_channel_id
            await ctx.respond("Hodnota nastavena do databáze.", ephemeral=True)
            return

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(AutoVoice(bot))
