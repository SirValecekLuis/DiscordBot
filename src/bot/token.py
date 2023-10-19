import json
import sys

# returns a discord token
def get_token() -> str:

    # try to load the config file into 'conf' dictionary
    # TODO would probably be ideal to load from pydantic settings or something like that
    conf_filename = "Data/conf.json"
    try:
        with open(conf_filename) as f:
            conf = json.load(f)

    # handle a case where the file doesn't exist
    except FileNotFoundError:
        print(f"File {get_token} doesn't exist,"
              "you need to create it first!")
        sys.exit()

    # handle any error that could've occured
    except Exception as e:
        print(f"An error has occurred: {e}")

    # check if there is a token set in the config
    if "Token" not in conf:
        print("You need to set your discord bot token in Data/conf.json\n"
              "Refer to documentation for further instructions")
        sys.exit()

    # return the Token string
    return conf["Token"]
