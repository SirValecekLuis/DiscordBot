"""Script to start the bot."""

import os
import discord
from discord.ext import commands

from database import Database
from settings import settings

# setup discord client intents
intents = discord.Intents.all()

# create discord client class instance
bot = commands.Bot(intents=intents)

# using Database class from database.py
db = Database(settings.database_login)


def load_cogs() -> None:
    """
    This function will load all the cogs based on the files from bot folder.
    :return: None
    """

    current_file = os.path.abspath(__file__)

    # Get the current file path
    current_dir = os.path.dirname(current_file)

    # "bot" folder path
    bot_dir = os.path.join(current_dir, "bot")

    # Checks if "bot" folder exists
    if not os.path.exists(bot_dir):
        print("Složka bot nebyla nalezena.")
        return

    # Get all python files in folder "bot"
    python_files = [file for file in os.listdir(bot_dir) if
                    file.endswith('.py') and os.path.isfile(os.path.join(bot_dir, file))]

    # Get names without .py
    cog_list = [os.path.splitext(file)[0] for file in python_files]

    # Remove __init__ as it is useless, and it would cause an error
    try:
        cog_list.remove("__init__")
    except ValueError:
        ...

    # Load every cog from cog_list
    for cog in cog_list:
        bot.load_extension(f"bot.{cog}")


# Run discord client with discord token from .env variable "TOKEN"
if __name__ == "__main__":
    load_cogs()
    bot.run(settings.bot_token)
