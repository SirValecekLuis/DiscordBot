"""This module is used to change and insert variables in DB via slash commands on discord."""
import discord
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


class DatabaseCommunication(commands.Cog):
    """This cog is for database communication and allows bot-developers to insert variable in DB via slash command."""
    def __init__(self, bot: discord.bot) -> None:
        self.bot = bot

    @commands.slash_command(name='insert-or-update-value',
                            description='Tento příkaz vloží či upraví proměnnou v DB.')
    @commands.has_permissions(administrator=True)
    async def insert_or_update_value(self,
                                     ctx: discord.ApplicationContext,
                                     name: str,
                                     value: str,
                                     value_type: discord.Option(
                                         str,
                                         description="Jakého typu je proměnná?",
                                         choices=["int", "float", "str"]
                                     )) -> None:
        """
        This command updates or insert a variable to Database.
        Throws error if value conversion was not successful.
        :param ctx: Slash command context
        :param name: Name of variable
        :param value: Value of variable
        :param value_type: Type of Variable as discord Option that ensures some of the given choices
        :return: None
        """

        try:
            # Type checking
            if value_type == "str":
                ...
            elif value_type == "int":
                value = int(value)
            elif value_type == "float":
                value = float(value)
            else:
                raise ValueError()
        except ValueError:
            # If something is wrong with value and value_type
            await ctx.respond(
                f"Nesprávná hodnota či nelze převést zadanou hodnotu {value} na daný datový typ {value_type}.",
                ephemeral=True)
        else:
            # Insert or update in MongoDB
            await db.insert_or_update_into_variables(name, value)

        await ctx.respond(f"Hodnota s názvnem {name} typu {value_type} a hodnotou {value} vložena/změněna úspěšně.",
                          ephemeral=True)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(DatabaseCommunication(bot))
