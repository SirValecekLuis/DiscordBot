"""This module is used to change and insert variables in DB via slash commands on discord."""
import discord
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


class DatabaseCommunication:
    def __init__(self, bot: discord.bot) -> None:
        self.bot = bot

    @commands.slash_command(name='insert-or-update-value',
                            description='Tento příkaz vloží či upraví proměnnou v DB.')
    @commands.has_permissions(administrator=True)
    async def insert_or_update_value(self, name: str, value: discord.Option()) -> None:
        ...

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(DatabaseCommunication(bot))
