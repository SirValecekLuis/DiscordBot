"""Cog that is supposed to add a record to user to database if specific word is triggered """
import discord
from discord.ext import commands
from discord.commands import Option
from start import db

"""
There is no issue to add a new counter, the function add_to_counter is made to add a counter to user if the user has
already a record in the database but without the specified counter. Then just simply fill the arguments which
are needed for add_to_counter func.
COUNTER = {"name_in_database": "name_to_show_for_user"}
"""
COUNTERS = {"counter_tobias": "Tobiáš",
            "counter_poli": "Poli/Olivka",
            }

poli_words = ["poli", "polim", "poliho", "polimu"]


async def add_to_counter(user_id: int, count: int, counter: str) -> None:
    """
    Function goes through all users and if user has a record, +1 is added to specific counter, if record is not
    found a new record is created.

    :param user_id: ID of author from discord message
    :param count: amount of counted words which should be added
    :param counter: string based on which counter is supposed to be added (via counters list above)
    :return: None
    """

    user = await db.find_user_from_database(user_id)  # Trying to find user based on user id, returns record or None
    if user:
        try:
            count_from_user = user[counter]  # Obtaining actual counter
            db.counter.update_one({"id": user_id}, {"$set": {counter: count_from_user + count}})
        except KeyError:  # If the counter is not part of database I add it to user and set to count
            db.counter.update_one({"id": user_id}, {"$set": {counter: count}})
        return
    else:
        # If user was not found, I will create a new one + add all counters
        db.counter.insert_one({"id": user_id})
        for counter_from_keys in COUNTERS.keys():
            if counter_from_keys == counter:  # If I find the same counter as was specified, I add count to counter
                db.counter.update_one({"id": user_id}, {"$set": {counter_from_keys: count}})
            else:
                db.counter.update_one({"id": user_id}, {"$set": {counter_from_keys: 0}})


async def count_words(message: str, words: list) -> int:
    """
    this function is supposed how many specified words are in given message.
    :param message: text from discord message
    :param words: list of words which are to be found and counted from message
    :return: amount of found words
    """
    count = 0
    message = message.split()  # It needs to be split due to finding specific words

    for word in words:
        count += message.count(word)

    return count


class Counter(commands.Cog):
    def __init__(self, bot_ref: discord.Bot) -> None:
        self.bot = bot_ref

    @commands.slash_command(name="counters", description="Vypíše počítadla, @uživatel pro vypsání jeho statistik")
    async def counters(self, ctx, member: Option(discord.Member, "Uživatel", required=False, default=None)) -> None:
        """
        Counters is a slash command which can be used with or without 1 optional parameter.
        -> If command is used without a parameter, then author of command is found in database and gets message
        from bot with statistics
        -> If command has a parameter then statistics of tagged user are shown from bot
        :param ctx: context of slash command
        :param member: OPTIONAL, tagged member to show his statistics
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
                await ctx.respond(f"Nemáš žádný záznam", ephemeral=True)
            return

        # Creating message for bot to send and asking for data from database
        text = "Tvoje počítadla\n"
        for counter, counter_text in COUNTERS.items():
            try:
                text += f"{counter_text}: {user_from_database[counter]}\n"
            except KeyError:
                text += f"{counter_text}: {0}\n"

        await ctx.respond(text, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        lowered_message = message.content.lower()
        tobias_count = lowered_message.count("tobiáš")
        poli_count = await count_words(lowered_message, poli_words) + lowered_message.count("olivk")

        if tobias_count > 0:
            await add_to_counter(message.author.id, tobias_count, "counter_tobias")
        if poli_count > 0:
            await add_to_counter(message.author.id, poli_count, "counter_poli")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Counter(bot))
