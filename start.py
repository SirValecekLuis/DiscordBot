import discord
import dotenv
import os

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

# load .env variables
dotenv.load_dotenv()

# run discord client with discrod token from .env variable "TOKEN"
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
