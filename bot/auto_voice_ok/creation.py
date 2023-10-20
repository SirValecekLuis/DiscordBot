import discord


async def create_new_channel(user: discord.Member):
    discord_server = user.guild

    # create the voice channel name from username or nickname
    new_channel_name = user.name + "'s channel"
    if user.nick is not None:
        new_channel_name = user.nick + "'s channel"

    created_channel = await discord_server.create_voice_channel(new_channel_name)

    await user.move_to(created_channel)
