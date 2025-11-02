"""This cog is for webkredit related commands."""

import uuid
import datetime

import discord
from discord.ext import commands, tasks
from webkredit import api

from error_handling import send_error_message_to_user
from start import db


class DatePickerView(discord.ui.View):
    """A view with buttons for picking a date."""

    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        days_cz = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek"]
        today = datetime.date.today()
        result = []
        current_day = today

        # Get next 5 weekdays
        while len(result) < 5:
            weekday = current_day.weekday()
            if weekday < 5:
                result.append(current_day)
            current_day += datetime.timedelta(days=1)

        # Format the day name and date
        result = [(days_cz[d.weekday()], d.strftime("%d.%m.%Y")) for d in result]
        for name, d in result:
            label = f"{name} {d}"
            self.add_item(DateButton(label=label, value=d, user=user))


class MealPickerSelect(discord.ui.Select):
    """A select menu for picking meals to monitor."""

    def __init__(self, meals: list[api.Meal], date_str: str, user: discord.User):
        self.date_str = date_str
        self.user = user

        options = []
        for meal in meals:
            label = f"{'XXL' if meal.is_xxl else ''} {meal.number}. {meal.name}"
            if len(label) > 100:
                label = label[:97] + "..."
            options.append(discord.SelectOption(label=label, value=str(meal.number)))

        super().__init__(
            placeholder="Vyber jídla, které chceš hlídat",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_meals = self.values
        req_id = str(uuid.uuid4())[:12]

        await interaction.response.edit_message(
            content=f"Jakmile jedno z jídel {', '.join(selected_meals)} bude dostupné, dostaneš zprávu!"
                    f"\nPokud budeš chtít hlídání zrušit, napiš soukromou zprávu botovi do které napíšeš **!{req_id}**",
            view=None)

        # Register the meal notification
        day, month, year = list(map(int, self.date_str.split(".")))
        selected_meals = [int(meal) for meal in selected_meals]
        await db.insert_one("webkredit",
                            {"user_id": self.user.id, "year": year, "month": month, "day": day,
                             "meal_numbers": selected_meals, "req_id": req_id})


class MealPickerView(discord.ui.View):
    """A view containing the meal picker select menu."""

    def __init__(self, meals: list[api.Meal], date_str: str, user: discord.User):
        super().__init__(timeout=60)
        self.add_item(MealPickerSelect(meals, date_str, user))


class DateButton(discord.ui.Button):
    """A button representing a specific date."""

    def __init__(self, label: str, value: str, user: discord.User):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.value = value
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        day, month, year = list(map(int, self.value.split(".")))
        url = api.get_webkredit_url(year, month, day)
        meals = api.get_meals(url)

        if len(meals) == 0:
            await interaction.response.send_message(
                f"❌ Pro zadaný den **{self.value}** není jídelníček. Pravděpodobně jde o státní svátek.", ephemeral=True
            )
            return

        meal_view = MealPickerView(meals, self.value, self.user)

        # Edit the original message instead of creating a new one
        await interaction.response.edit_message(
            content="Vyber si jídlo, které chceš hlídat:", view=meal_view
        )


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
                    await message.channel.send("Tvoje hlídání obědů s tímto ID bylo zrušeno.")
                else:
                    await message.channel.send("Nemáš právo na smazání těchto obědů.")

    @tasks.loop(seconds=5)
    async def check_webkredit(self):
        """This task checks for webkredit meal availability and notifies users.
        :return: None
        """
        for meal in await db.find("webkredit", {}):
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
                     f"(Dostupných porcí: {meal.available if meal.available is not None else 'neomezeno'}) "
                     f"Burza: {'ano' if meal.in_exchange else 'ne'}"
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
    async def webkredit(self, ctx: discord.ApplicationContext) -> None:
        """An interactive version of the webkredit command using dropdowns and date picker.
        :param ctx: Context of slash command
        :return: None
        """
        # Check that user has maximum 3 active webkredit notifications
        user_meal_count = await db.find("webkredit", {"user_id": ctx.author.id})
        user_meal_count = len(user_meal_count)
        if user_meal_count >= 3:
            await ctx.respond("Máš už maximální počet 3 aktivních hlídačků na obědy.", ephemeral=True)
            return

        view = DatePickerView(ctx.user)
        await ctx.respond("Vyber si den s obědem a musíš mít povolené soukromé zprávy, aby tě bot mohl kontaktovat.",
                          ephemeral=True, view=view)

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
