"""Cog that prints info about the bot logging in."""

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user


class LoginInfo(commands.Cog):
    """This cog is just an information for developers to know the bot was recognized by discord API and is running."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Listener when bot turns on and is running.
        :return: None
        """
        print(f"Logged in as {self.bot.user}")

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
    bot.add_cog(LoginInfo(bot))
