"""Cog that sends a welcome message to a user when he joins the server."""

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user

WELCOME_STR = "Cus picus"


class WelcomeMessage(commands.Cog):
    """This is a Cog that will send user a message to PM when joins our DC."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Listener that sends user a message on joining a discord server.
        :param member: Member that joined the discord server
        :return: None
        """
        await member.send(content=WELCOME_STR)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        """Handles all errors that can happen in a cog and then sends them to send_error_message_to_user to deal with
        any type of error.
        :param ctx: Context of slash command
        :param error: Error that happened in a cog
        :return: None
        """
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(WelcomeMessage(bot))
