import json
import sys

# import client from bot, bot.py sets up the client
from bot import client

# try to load the config file into 'conf' dictionary
# TODO would probably be ideal to load from pydantic settings or something like that
CONF_FILENAME = "Data/conf.json"
try:
    with open(CONF_FILENAME) as f:
        conf = json.load(f)

# handle a case where the file doesn't exist

except FileNotFoundError:
    print(f"File {CONF_FILENAME} doesn't exist, you need to create it first!")
    sys.exit()

# handle any error that could've occured
except Exception as e:
    print(f"An error has occurred: {e}")

# check if there is a token set in the config
if "Token" not in conf:
    print("You need to set your discord bot token in Data/conf.json\n"
          "Refer to documentation for further instructions")
    sys.exit()


# run discord client
if __name__ == "__main__":
    client.run(conf["Token"])
