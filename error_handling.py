"""This file will be responsible for sending error messages whenever a command unexpectedly fails"""
import discord


# TODO: Test if the function is triggered by errors such as no permission or not
async def send_error_message_to_user(ctx: discord.ApplicationContext, error: discord.DiscordException) -> None:
    """
    Sends back to user a warning when slash command fails and info in bot-development channel
    :param ctx: context from slash command
    :param error: raised exception from slash command
    :return: None
    """
    error_message = (f"Uživatel {ctx.user.mention} použil příkaz **->{ctx.command.qualified_name}<-** "
                     f"který selhal.\nChyba: **{repr(error)}**")

    try:
        await ctx.respond("Nastala neočekávaná chyba při použití toho příkazu, prosím, kontakujte někoho z "
                          "moderátorů.", ephemeral=True)
        guild = ctx.guild
        channel = discord.utils.get(guild.channels, name="bot-development")
        await channel.send(error_message)
    except AttributeError:
        # TODO: implement logging? For now it prints in a console when bot-development channel is not found
        print("Channel bot-development neexistuje, printuji do konzole\n")
        print(error_message)
