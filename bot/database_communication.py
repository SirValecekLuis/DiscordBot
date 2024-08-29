"""This module is used to change and insert variables in DB via slash commands on discord."""

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


class DatabaseCommunication(commands.Cog):
    """This cog is for database communication and allows bot-developers to insert variable in DB via slash command."""

    def __init__(self, bot: discord.bot) -> None:
        self.bot = bot

    @commands.slash_command(name="insert-or-update-value", description="Tento příkaz vloží či upraví proměnnou v DB.")
    @commands.has_permissions(administrator=True)
    async def insert_or_update_value(
            self,
            ctx: discord.ApplicationContext,
            name: str,
            value: str,
            value_type: discord.Option(
                str,
                description="Jakého typu je proměnná?",
                choices=["int", "float", "str"],
            ),
    ) -> None:
        """This command updates or insert a variable to Database.
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
                raise ValueError
        except ValueError:
            # If something is wrong with value and value_type
            await ctx.respond(
                f"Nesprávná hodnota či nelze převést zadanou hodnotu {value} na daný datový typ {value_type}.",
                ephemeral=True,
            )
        else:
            # Insert or update in MongoDB
            await db.insert_or_update_into_variables(name, value)

        await ctx.respond(
            f"Hodnota s názvnem {name} typu {value_type} a hodnotou {value} vložena/změněna úspěšně.",
            ephemeral=True,
        )

    @commands.slash_command(name="print-value-from-db", description="Tento příkaz ti ukáže hodnotu proměnné z DB.")
    @commands.has_permissions(administrator=True)
    async def print_value_from_db(self, ctx: discord.ApplicationContext, name: str) -> None:
        """
        This will return a value from DB based on a name that you search for.
        :param ctx: Command context
        :param name: Name of a variable
        :return: None, sends a message with an error or with variable value.
        """

        value = await db.get_variable_from_variables(name)

        if value is None:
            await ctx.respond(
                "Proměnná s tímto názvem nebyla nalezena. "
                "Použijte příkaz /print-names-from-db pro veškeré názvy proměnných aktuálně v DB.", ephemeral=True)
        else:
            await ctx.respond(f"Proměnná se jménem {name} má hodnotu |{value}|.", ephemeral=True)

    @commands.slash_command(name="print-names-from-db",
                            description="Tento příkaz ti vypíše všechny názvy proměnných v DB.")
    @commands.has_permissions(administrator=True)
    async def print_names_from_db(self, ctx: discord.ApplicationContext) -> None:
        """
        This will show an exhaustive list of all variable names in variables collection.
        :param ctx: Command context
        :return: None, sends a message with all names
        """

        text = "| "

        for var in await db.get_all_variables_names():
            text += var
            text += " | "

        await ctx.respond(text, ephemeral=True)

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
    bot.add_cog(DatabaseCommunication(bot))
