"""Cog that sends welcome message to user when he joins the server."""
import discord
from discord.ext import commands

welcome_str = "Vítej na Discord serveru"


class WelcomeMessage(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await member.send(content=welcome_str)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(WelcomeMessage(bot))
