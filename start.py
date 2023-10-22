"""Script to start the bot."""
import discord
from discord.ext import commands
from pymongo import MongoClient
from settings import settings

# Database setting
client = MongoClient(settings.database_login)
db = client["DiscordBot"]  # db.Counter to access section in DB for counter

# setup discord client intents
intents = discord.Intents.all()

# create discord client class instance
bot = commands.Bot(intents=intents)

# list of all cog modules
cog_list = [
    "login_info",
    "counter",
    "poop",
    "wakeup",
    "auto_voice",
]

# load every cog in cog_list
for cog in cog_list:
    bot.load_extension(f"bot.{cog}")

# run discord client with discord token from .env variable "TOKEN"
if __name__ == "__main__":
    bot.run(settings.bot_token)
