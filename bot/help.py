"""This module is for help commands bot will provide."""

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user


class Help(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name='github',
                            description='Tento příkaz ti pošle náš link na github!')
    async def github(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("https://github.com/SirValecekLuis/DiscordBot", ephemeral=True)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Help(bot))
