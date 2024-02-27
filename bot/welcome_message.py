"""Cog that sends a welcome message to a user when he joins the server."""
import discord
from discord.ext import commands

WELCOME_STR = "Cus picus"


class WelcomeMessage(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await member.send(content=WELCOME_STR)

        """Listener that sends user a message on joining a discord server.

        :param member: member that joined the discord server
        :return: None
        """


def setup(bot: discord.Bot) -> None:
    bot.add_cog(WelcomeMessage(bot))
