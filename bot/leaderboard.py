"""Cog that enables the user to see the counter-leaderboard."""

import discord
from discord.commands import Option
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


async def get_leaderboard(entries: list) -> dict:
    """Queries the database for counter-statistics, sums them
    and returns a sorted dictionary<user_id, counter_sum>.

    :param entries: List containing entries from the database
    :return: Dict containing the sum and user id
    """
    # sums the counters and stores the value into leaderboard dict
    leaderboard = {}
    for entry in entries:
        leaderboard[entry["id"]] = sum(value for key, value in entry.items() if key != "id")

    # sorts the leaderboard dict
    return dict(sorted(leaderboard.items(), key=lambda pair: pair[1], reverse=True))


class CounterLeaderboard(commands.Cog):
    """This cog handles the leaderboard of discord members."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="leaderboard", description="Vypíše uživateli žebříček počítadla v rozsahu 1-40 max.")
    async def get_counter_leaderboard(self,
                                      ctx: discord.ApplicationContext,
                                      user_limit: Option(int,
                                                         description="Celé číslo v rozmezí 1-20",
                                                         required=False)) -> None:
        """Sends a list of people with the highest sum of counters to the user

        :param ctx: Context of slash command
        :param user_limit: optional limit on how many people will be displayed
        :return: None
        """
        # retrieves counter-stats from the database, sums them and sorts them
        leaderboard = await get_leaderboard(
            list(db.counter.find({}, {"_id": 0, "id": 1, "counter_tobias": 1, "counter_poli": 1})),
        )

        # sets the limit on how many entries will be displayed
        limit: int = 20

        # tries to parse and use the user defined limit
        if user_limit:
            # apply hard limit of 40
            if 40 >= user_limit >= 1:
                limit = user_limit

        # create a response string
        response: str = "Současný žebříček součtu počítadel:\n"

        # build the response by adding leaderboard entries to it
        try:
            for index, (key, value) in zip(range(1, limit + 1), leaderboard.items()):
                response += f"{index}. <@{key}>: {value}\n"

            # send the response to the user
            await ctx.respond(response, ephemeral=True)
        except AttributeError:
            # notify user of an error in displaying the leaderboard
            await ctx.respond(
                "Leadboard nemohl být načten, pravděpodobně kvůli chybě ze strany databáze.",
                ephemeral=True,
            )
            return

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
    bot.add_cog(CounterLeaderboard(bot))
