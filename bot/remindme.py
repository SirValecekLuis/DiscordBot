"""This is a module for remind command that will be something like a calendar for people on discord."""
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
import discord
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


class Remindme(commands.Cog):
    """This class handles reminders that can discord user use as a calendar."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This listener is checking the database every second if should someone remind or not.
        :return: None
        """
        while True:
            # TODO: Check for reminders
            await asyncio.sleep(1)

    @commands.slash_command(name="remindme",
                            description="Tento příkaz ti pošle zprávu za určitou dobu s nějakou přípomínkou. "
                                        "Formát např. 13.7.2024 12:00:00")
    async def remindme(self, ctx: discord.ApplicationContext, date: str, text_to_remind: str) -> None:
        """
        This command can be called and will store a reminder in database.
        :param ctx: Slash command context
        :param date: Date when to remind
        :param text_to_remind: Text to remind
        :return: None
        """
        try:
            date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

            # Prague
            prague_tz = ZoneInfo("Europe/Prague")

            # Change time zone
            date_tz = date.replace(tzinfo=prague_tz)

            # Get time from that time zone
            time_now = datetime.now(prague_tz)

            print(time_now, "||||", date_tz)

            # if the time is in the past, we do not want to add that in the database
            if date_tz <= time_now:
                await ctx.respond("Zadané datum je v minulosti. Prosím, zadejte budoucí datum.", ephemeral=True)

            # If everything is good, add the reminder in DB
            await db.insert_reminder(ctx.user.id, date, text_to_remind)

            # Tell the user it was added
            await ctx.respond("Do databáze byla přidána událost k připomenutí. "
                              "Použij /reminders k vidění všech svých kalendářních připomínek.", ephemeral=True)
        except ValueError:
            await ctx.respond(
                "Neplatné datum. Datum musí být ve formátu '13.7.2024 12:00:00'",
                ephemeral=True)

    @commands.slash_command(name="reminders",
                            description="Tento příkaz ti vypíše seznam všech svých kalendářních připomínek.")
    async def reminders(self, ctx: discord.ApplicationContext) -> None:
        """
        Sends to user all the reminders.
        :param ctx: Slash command context
        :return: None
        """
        results = await db.get_reminders(ctx.user.id)
        if len(results) == 0:
            await ctx.respond("Nemáš žádné připomínky.", ephemeral=True)

        text = ""

        for index, reminder in enumerate(results):
            text += f"Index: {index} Datum: {reminder['date']} Text: {reminder['text']}\n"

        await ctx.respond(f"Výčet tvých připomínek:\n{text}", ephemeral=True)

    @commands.slash_command(name="remove-reminder",
                            description="Tento příkaz ti vypíše seznam všech svých kalendářních připomínek.")
    async def remove_reminder(self, ctx: discord.ApplicationContext, reminder_id: int) -> None:
        """
        Tries to remove a reminder from DB if user wishes to remove it.
        :param ctx: Command context
        :param reminder_id: ID of a reminder to remove
        :return: None
        """
        # TODO: Implement this
        await ctx.respond("Reminder úspěšně smazán.", ephemeral=True)

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
    bot.add_cog(Remindme(bot))
