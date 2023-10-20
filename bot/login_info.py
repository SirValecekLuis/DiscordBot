"""Cog that prints info about the bot logging in."""
import discord
from discord.ext import commands


class LoginInfo(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"Logged in as {self.bot.user}")

def setup(bot: discord.Bot) -> None:
    bot.add_cog(LoginInfo(bot))
