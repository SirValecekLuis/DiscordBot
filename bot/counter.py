"""Cog that is supposed to add a record to user to database if specific word is triggered."""
import discord
from discord.commands import Option
from discord.ext import commands

from start import db
from error_handling import send_error_message_to_user

"""
There is no issue to add a new counter, the function add_to_counter is made to add a counter to user if the user has
already a record in the database but without the specified counter. Then just simply fill the arguments which
are needed for add_to_counter func.
COUNTERS = {"name_in_database": "name_to_show_for_user"}
"""
COUNTERS = {"counter_tobias": "Tobiáš",
            "counter_poli": "Poli/Olivka",
            }

POLI_WORDS = ["poli", "polim", "poliho", "polimu"]


async def add_to_counter(user_id: int, count: int, counter: str) -> None:
    """Find user's record and add count to their counter.

    If the user doesn't have any record in the database, a new one is created.

    :param user_id: ID of author from discord message
    :param count: amount of counted words which should be added
    :param counter: string based on which counter is supposed to be added (via counters list above)
    :return: None
    """
    user = await db.find_user_from_database(user_id)  # Trying to find user based on user id, returns record or None
    if user:
        count_from_user = user.get(counter)  # Obtaining actual counter
        if count_from_user:
            db.counter.update_one({"id": user_id}, {"$set": {counter: count_from_user + count}})
        else:
            db.counter.update_one({"id": user_id}, {"$set": {counter: count}})
        return

    # If user was not found, I will create a new one + add all counters
    db.counter.insert_one({"id": user_id})
    for counter_from_keys in COUNTERS:
        if counter_from_keys == counter:  # If I find the same counter as was specified, I add count to counter
            db.counter.update_one({"id": user_id}, {"$set": {counter_from_keys: count}})
        else:
            db.counter.update_one({"id": user_id}, {"$set": {counter_from_keys: 0}})


async def count_words(message: str, words: list) -> int:
    """Count the amount of words in message.

    :param message: text from discord message
    :param words: list of words which are to be found and counted from message
    :return: amount of found words
    """
    count = 0
    message = message.split()  # It needs to be split due to finding specific words

    for word in words:
        count += message.count(word)

    return count


async def add_emote(message: discord.Message, emote_name: str) -> None:
    """Add a reaction to the message.

    :param message: Discord message
    :param emote_name: name of the emote to add
    """
    try:
        guild = message.guild
        emoji = discord.utils.get(guild.emojis, name=emote_name)
        await message.add_reaction(emoji)
    except discord.errors.InvalidArgument as e:
        # TODO: add error logging for this
        print(f"You can ignore this warning, it comes from typing Tobiáš or Poli with missing emote.\n{e}")


class Counter(commands.Cog):
    """Cog to initialize word counter."""

    def __init__(self, bot_ref: discord.Bot) -> None:
        self.bot = bot_ref

    @commands.slash_command(name="counters", description="Vypíše počítadla, @uživatel pro vypsání jeho statistik")
    async def counters(self, ctx: discord.ApplicationContext,
                       member: Option(discord.Member, "Uživatel", required=False, default=None)) -> None:
        """Slash command that writes out counter of a specific user.

        If the member option is provided, the requested member is queried from the database. If not provided, the
        member calling the command is queried.

        :param ctx: context of slash command
        :param member: tagged member to show his statistics
        :return: None
        """
        user_id = ctx.user.id  # ID of author
        if member:  # If optional parameter is filled then I switch ID to tagged member
            user_id = member.id

        user_from_database = await db.find_user_from_database(user_id)  # User from database

        if user_from_database is None:  # If user has no record in database
            if member:
                await ctx.respond(f"Uživatel {member.mention} nemá žádný záznam.", ephemeral=True)
            else:
                await ctx.respond("Nemáš žádný záznam", ephemeral=True)
            return

        # Creating message for bot to send and asking for data from database
        text = "Tvoje počítadla\n"
        for counter, counter_text in COUNTERS.items():
            count_from_user = user_from_database.get(counter)
            if count_from_user is None:
                text += f"{counter_text}: {count_from_user}\n"
            else:
                text += f"{counter_text}: {0}\n"

        await ctx.respond(text, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        lowered_message = message.content.lower()
        tobias_count = lowered_message.count("tobiáš")
        poli_count = await count_words(lowered_message, POLI_WORDS) + lowered_message.count("olivk")

        if tobias_count > 0:
            await add_to_counter(message.author.id, tobias_count, "counter_tobias")
            await add_emote(message, "TrollDespair")
            await add_emote(message, "MonkaGun")
        if poli_count > 0:
            await add_to_counter(message.author.id, poli_count, "counter_poli")
            await add_emote(message, "olivkacursed")

    async def on_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Counter(bot))
