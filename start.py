"""Script to start the bot."""
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

# list of all cog modules
cog_list = [
    "login_info",
    "counter",
    "auto_voice",
]

# load every cog in cog_list
for cog in cog_list:
    bot.load_extension(f"bot.{cog}")

# run discord client with discord token from .env variable "TOKEN"
if __name__ == "__main__":
    bot.run(settings.bot_token)
