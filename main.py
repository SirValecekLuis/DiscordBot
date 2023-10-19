import discord
import json

# import client from bot, bot.py sets up the client
from bot import client

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


# run discord client
if __name__ == "__main__":
    client.run(conf["Token"])
