"""Cog that prints info about the bot logging in."""
import discord
from discord.ext import commands


class LoginInfo(commands.Cog):
    """This cog is just an information for developers to know the bot was recognized by discord API and is running."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Listener when bot turns on and is running.
        :return: None
        """
        print(f"Logged in as {self.bot.user}")


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(LoginInfo(bot))
