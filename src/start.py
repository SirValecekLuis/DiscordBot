from bot.bot import client
from bot.token import get_token

# run discord client
if __name__ == "__main__":
    client.run(get_token())
