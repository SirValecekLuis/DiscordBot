"""Cog that sends a welcome message to a user when he joins the server."""
import discord
from discord.ext import commands

WELCOME_STR = "Cus picus"


class WelcomeMessage(commands.Cog):
    """This is a Cog that will send user a message to PM when joins our DC."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Listener that sends user a message on joining a discord server.
        :param member: Member that joined the discord server
        :return: None
        """
        await member.send(content=WELCOME_STR)


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(WelcomeMessage(bot))
