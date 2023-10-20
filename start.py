"""Script to start the bot."""
import discord

from settings import settings

# setup discord client intents
intents = discord.Intents.all()

# create discord client class instance
bot = discord.Bot(intents=intents)

# list of all cog modules
cog_list = [
    "login_info",
]

# load every cog in cog_list
for cog in cog_list:
    bot.load_extension(f"bot.{cog}")


# run discord client with discrod token from .env variable "TOKEN"
if __name__ == "__main__":
    bot.run(settings.bot_token)
