import discord


# creates and return a new channel for the user
async def create_new_channel(
    user: discord.Member,
    category: discord.CategoryChannel,
) -> discord.VoiceChannel:

    discord_server = user.guild

    # create the voice channel name from username or nickname
    new_channel_name = user.name
    if user.nick is not None:
        new_channel_name = user.nick
    new_channel_name += "'s channel"

    # create the new channel
    created_channel = await discord_server.create_voice_channel(name=new_channel_name, category=category)

    # move the user to the newly created channel
    await user.move_to(created_channel)

    # return the created channel
    return created_channel
