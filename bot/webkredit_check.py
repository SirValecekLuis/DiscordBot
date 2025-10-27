"""This cog is for webkredit related commands."""

import uuid
import datetime

import discord
from discord.ext import commands, tasks
from webkredit import api

from error_handling import send_error_message_to_user
from start import db


class Webkredit(commands.Cog):
    """This cog is for webkredit related commands."""

    def __init__(self, bot: discord.bot) -> None:
        self.bot = bot
        self.check_webkredit.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listens for messages to allow users to cancel their webkredit meal notifications.
        :param message: The message sent by the user.
        :return: None
        """
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.startswith("!"):
                req_id = message.content[1:].strip()
                meal = await db.find_one("webkredit", {"req_id": req_id})
                if meal is None:
                    await message.channel.send("Neplatné ID pro zrušení hlídání obědů.")
                    return

                if meal["user_id"] == message.author.id:
                    await db.delete_one("webkredit", {"_id": meal["_id"]})
                    await message.channel.send("Tvoje hlídání obědů bylo zrušeno.")
                else:
                    await message.channel.send("Nemáš právo na smazání těchto obědů.")

    @tasks.loop(seconds=5)
    async def check_webkredit(self):
        """This task checks for webkredit meal availability and notifies users.
        :return: None
        """
        for meal in await db.find("webkredit", {}):
            print(meal)
            user: discord.User = self.bot.get_user(meal["user_id"])
            year = meal["year"]
            month = meal["month"]
            day = meal["day"]
            meal_numbers = meal["meal_numbers"]

            date = datetime.date.fromisoformat(f"{year}-{month:02}-{day:02}")
            if datetime.date.today() > date:
                await db.delete_one("webkredit", {"_id": meal["_id"]})
                continue

            url = api.get_webkredit_url(year, month, day)
            meals = api.get_meals(url)

            if len(meals) == 0:
                continue

            available_meals = api.find_available_meals(meals, meal_numbers)
            if available_meals:
                meal_list = "\n".join(
                    [f"Jídlo {meal.number}. {meal.name} "
                     f"(Dostupných porcí: {meal.available if meal.available is not None else 'neomezeno'})"
                     for meal in available_meals])
                if user is not None:
                    try:
                        await user.send(
                            f"\n{user.mention} Jídla, která jsi hlídal(a) na {day}.{month}.{year} "
                            f"jsou nyní dostupná:\n{meal_list}")
                    except discord.Forbidden:
                        pass  # User has DMs disabled
                await db.delete_one("webkredit", {"_id": meal["_id"]})

    @commands.slash_command(name="webkredit", description="Zaregistruj si hlídáček na oběd v menze!")
    async def webkredit(self, ctx: discord.ApplicationContext,
                        date: discord.Option(
                            str,
                            description="Datum ve formátu den.měsíc.rok, např. 25.10.2025",
                            required=True,
                            name="datum",
                            min_length=8,
                            max_length=10),
                        meals: discord.Option(
                            str,
                            description="Čísla jídel oddělená čárkou, např. 1,2,3 (maximálně 10 jídel)",
                            required=True,
                            name="jídla",
                            min_length=1,
                            max_length=100
                        )) -> None:
        """This command registers a user for webkredit meal notifications.
        :return: None
        """
        # Check that user has maximum 3 active webkredit notifications
        user_meal_count = await db.find("webkredit", {"user_id": ctx.author.id})
        user_meal_count = len(user_meal_count)
        if user_meal_count >= 3:
            await ctx.respond("Máš už maximální počet 3 aktivních hlídačků na obědy.", ephemeral=True)
            return

        # Validate date
        year, month, day = api.get_day_check(date)
        if year is None or month is None or day is None:
            await ctx.respond("Neplatný formát data. Použij formát 25.10.2025", ephemeral=True)
            return

        # Check that date is not in the past
        date = datetime.date.fromisoformat(f"{year}-{month:02}-{day:02}")
        if datetime.date.today() > date:
            await ctx.respond("Datum nemůže být v minulosti.", ephemeral=True)
            return

        # Validate meal numbers
        meal_numbers = api.get_meal_numbers_check(meals.split(","))
        if meal_numbers is None:
            await ctx.respond(
                "Neplatný formát čísel jídel. Použij čísla oddělená čárkou, např. 1,2,3 a čísla mohou být v rozsahu 1-10 pouze.",
                ephemeral=True)
            return

        # Check that meals are available for the given day
        url = api.get_webkredit_url(year, month, day)
        available_meals = api.get_meals(url)
        if len(available_meals) == 0:
            await ctx.respond("Pro zadaný den není jídelníček.", ephemeral=True)
            return

        # Register the meal notification
        req_id = str(uuid.uuid4())[:12]
        await db.insert_one("webkredit", {"user_id": ctx.author.id, "year": year, "month": month, "day": day,
                                          "meal_numbers": meal_numbers, "req_id": req_id})

        # Send confirmation to user via DM and print the meals being monitored that user requested
        formatted_string_meals = ""
        for number in meal_numbers:
            for meal in available_meals:
                if meal.number == number:
                    formatted_string_meals += f"{str(meal)}\n"

        await ctx.user.send(
            f"Tvoje hlídání obědů v menze bylo úspěšně zaregistrováno! Pro zrušení tohoto hlídání pošli botovi zprávu !{req_id}\n"
            f"Na den {day}.{month}.{year} budou hlídána tato jídla: \n{formatted_string_meals}")

        await ctx.respond("Hlídání obědů bylo úspěšně zaregistrováno! Podrobnosti ti byly poslány do DM.",
                          ephemeral=True)

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
    bot.add_cog(Webkredit(bot))
