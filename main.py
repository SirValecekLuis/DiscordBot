import discord
import json

# try to load the config file into 'conf' dictionary
confFileName = "Data/conf.json"
try:
    with open(confFileName, 'r') as confFile:
        conf = json.load(confFile)

# handle a case where the file doesn't exist

except FileNotFoundError:
    print(f"File {confFileName} doesn't exist, you need to create it first!")
    exit()

# handle any error that could've occured
except Exception as e:
    print(f"An error has occured: {str(e)}")

# check if there is a token set in the config
if "Token" not in conf:
    print("You need to set your discord bot token in Data/conf.json")
    print("Refer to documentation for further instructions")
    exit()

# setup discord client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# setup on_ready listener
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


# setup on_message event listener
@client.event
async def on_message(message):
    print(f'{message.author}: {message.content}')

# run discord client
client.run(conf["Token"])
