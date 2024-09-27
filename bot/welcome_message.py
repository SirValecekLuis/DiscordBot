"""Cog that sends a welcome message to a user when he joins the server."""

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user

WELCOME_STR = '''Vítej v komunitě oboru informatiky, u nás najdeš vypracované \
materiály z minulých let v pinned messages.
Budeme rádi, když budete sdílet náš server mezi spolužáky.'''

DISCORD_URL_LINK = 'https://discord.gg/fei-informatika'


class WelcomeMessage(commands.Cog):
    """This is a Cog that will send user a message to PM when joins our DC."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Listener that sends user a message on joining a discord server.
        :param member: Member that joined the discord server
        :return: None
        """

        guild = member.guild

        if guild.premium_tier >= 3:
            await member.send(content=f"{WELCOME_STR} {DISCORD_URL_LINK}")

        else:
            await member.send(content=f"{WELCOME_STR}")

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        """Handles all errors that can happen in a cog and then sends them to send_error_message_to_user to deal with
        any type of error.
        :param ctx: Context of slash command
        :param error: Error that happened in a cog
        :return: None
        """
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(WelcomeMessage(bot))
