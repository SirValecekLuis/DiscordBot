"""Cog that is supposed to add a record to user to database if specific word is triggered """
import discord
from discord.ext import commands
from start import db

"""
There is no issue to add a new counter, the function add_to_counter is made to add a counter to user if the user has
already a record in the database but without the specified counter. Then just simply fill the arguments which
are needed for add_to_counter func.
"""
COUNTERS = [
    "counter_tobias",
    "counter_poli",
]

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

    for user in db.Counter.find():
        if user["id"] == user_id:
            try:
                count_from_user = user[counter]  # Obtaining actual counter
                db.Counter.update_one({"id": user_id}, {"$set": {counter: count_from_user + count}})  # Updating counter
            except KeyError:  # If the counter is not part of database I add it to user and set to count
                db.Counter.update_one({"id": user_id}, {"$set": {counter: count}})
            return
    else:
        # If user was not found, I will create a new one + add all counters
        db.Counter.insert_one({"id": user_id})
        for counter_from_list in COUNTERS:
            if counter_from_list == counter:  # If I find the same counter as was specified, I add count to counter
                db.Counter.update_one({"id": user_id}, {"$set": {counter_from_list: count}})
            else:  # Else I set counter to 0 bud it is nice to have all records set to 0 immediately
                db.Counter.update_one({"id": user_id}, {"$set": {counter_from_list: 0}})


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
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        lowered_message = message.content.lower()
        tobias_count = lowered_message.count("tobiáš")
        poli_count = await count_words(lowered_message, poli_words) + lowered_message.count("olivk")

        if tobias_count > 0:
            await add_to_counter(message.author.id, tobias_count, "counter_tobias")
        if poli_count > 0:
            await add_to_counter(message.author.id, poli_count, "counter_poli")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Counter(bot))
