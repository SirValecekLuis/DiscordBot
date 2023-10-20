"""Cog waiting if user writes "tobiáš" in sentence and if yes, writes +1 to counter based on user ID """
import discord
from discord.ext import commands
from start import db

counters = [
    "counter_tobias",
    "counter_poli",
]


def add_to_counter(user_id: int, count: int, counter: str) -> None:
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
            except KeyError:    # If the counter is not part of database I add it to user and set to count
                db.Counter.update_one({"id": user_id}, {"$set": {counter: count}})
            return
    else:
        # If user was not found, I will create a new one + add all counters
        db.Counter.insert_one({"id": user_id})
        for counter_from_list in counters:  # Going through all counters
            if counter_from_list == counter:  # If I find the same counter as was specified, I add count to counter
                db.Counter.update_one({"id": user_id}, {"$set": {counter_from_list: count}})
            else:   # Else I set counter to 0 bud it is nice to have all records set to 0 immediately
                db.Counter.update_one({"id": user_id}, {"$set": {counter_from_list: 0}})


class Counter(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """ This part needs to be reworked in the future, not the best way to do this """
        lowered_message = message.content.lower()
        tobias_count = lowered_message.count("tobiáš")
        poli_count = lowered_message.split().count("poli") + lowered_message.count("olivk")

        if tobias_count > 0:
            add_to_counter(message.author.id, tobias_count, "counter_tobias")
        if poli_count > 0:
            add_to_counter(message.author.id, poli_count, "counter_poli")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Counter(bot))
