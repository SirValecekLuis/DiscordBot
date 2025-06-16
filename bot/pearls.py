"""Cog for detecting and posting new pearls (funny answers from APPS subject)."""

from typing import Dict, List, Optional, TypeAlias
import discord
import aiohttp
from discord.ext import commands, tasks
from bs4 import BeautifulSoup, Comment

from error_handling import send_error_message_to_user
from start import db

Answers: TypeAlias = List[Dict[str, Optional[str]]]


class Pearls(commands.Cog):
    """Class periodically looks for changes on the APPS subject website."""

    def __init__(self, bot_ref: discord.Bot) -> None:
        self.bot = bot_ref
        self.scrape_page.start()

    @tasks.loop(hours=1.0)
    async def scrape_page(self) -> None:
        """Task loop for checking new pearls on the website.
        :return: None
        """

        # Get the ID of channel and warn that bot_channel_id or apps_channel_id does not exist
        apps_channel_id = await db.find_one("variables", {}, "apps_channel_id")
        if apps_channel_id is None:
            bot_channel_id = await db.find_one("variables", {}, "bot_channel_id")
            if bot_channel_id is None:
                raise Exception("bot_channel_id není nastaveno.")
            bot_channel = self.bot.get_channel(bot_channel_id) or await self.bot.fetch_channel(bot_channel_id)
            await bot_channel.send("apps_channel_id není nastaveno!")
            return

        pearls = await self.get_all_pearls()
        # Exclude _id from output
        db_pearls = await db.find("pearls", {}, {"_id": 0})
        pearls = self.diff_pearls(pearls, db_pearls)

        if len(pearls) > 0:
            await db.insert_many("pearls", pearls)

            # If this is first insertion in DB, we wont print anything
            if len(db_pearls) == 0:
                return

            apps_channel = self.bot.get_channel(apps_channel_id) or await self.bot.fetch_channel(apps_channel_id)
            pluralized = "nové perly" if len(pearls) > 1 else "nová perla"
            message = f"## :skull: Přichází {pluralized}! :skull:\n"

            for pearl in pearls:
                # Send as quoted message
                answer = "> " + pearl["answer"].replace("\n", "\n> ")
                # If answers are longer than 2000 characters, send multiple messages
                if len(message) + len(answer) >= 2000:
                    await apps_channel.send(message)
                    message = ""
                message += answer + "\n\n"

            await apps_channel.send(message)

    def diff_pearls(self, lst1: Answers, lst2: Answers) -> Answers:
        """Compares list of answers from the website and from the database.
        Returns filtered list of answers that are present on the website but not in the database.
        :param lst1: List of answers from the website
        :param lst2: List of answers from the database
        :return: Answers
        """
        return [x for x in lst1 if x not in lst2]

    async def get_all_pearls(self) -> Answers:
        """Fetches pearls website and parses all answers with their respective logins."""
        pearls = []
        try:
            url = "https://poli.cs.vsb.cz/edu/apps/perly.html"
            async with aiohttp.ClientSession() as session:
                resp = await session.get(url=url,
                                         ssl=False,  # Someone just ignores renewing his SSL certificate...
                                         headers={
                                            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0)" +
                                            "Gecko/20100101 Firefox/139.0"
                                         })
                # Site encoding is not sent from the server, it must be set manually
                page = BeautifulSoup(await resp.text(encoding="utf-8"), "html5lib")
                main_div = page.find("div", "rr-main-div")
                if main_div:
                    # All answers are under the last horizontal line in the main div
                    answers = [x for x in main_div.find_all(recursive=False) if not x.find_next_sibling("hr")]
                    for answer in answers:
                        content = answer.text.strip()
                        # Some paragraphs are empty
                        if content:
                            # Find login from the upper comment
                            login = answer.find_previous(string=lambda x: isinstance(x, Comment))
                            pearls.append({
                                "answer": content,
                                "login": login.strip() if login else None
                            })
        except Exception:
            # Ignore possible server/parsing exceptions
            pass
        return pearls

    def cog_unload(self) -> None:
        """A special method that is called when the cog gets removed.
        :return: None
        """
        self.scrape_page.cancel()

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
    bot.add_cog(Pearls(bot))
