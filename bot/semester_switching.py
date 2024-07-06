"""This module is for semestr switching, wow."""
import discord
from discord.ext import commands
from discord import Option

from error_handling import send_error_message_to_user


class SemesterSwitching(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    def switch_categories(self, category: discord.CategoryChannel):
        print(category.name)

    @commands.slash_command(name='switch-semester',
                            description='Tento příkaz přehází semestry do správných kategorii pro nový semestr.')
    @commands.has_permissions(administrator=True)
    async def switch_semester(
            self,
            ctx: discord.ApplicationContext,
            semester_to_switch: Option(
                str,
                description="Zadejte semestr, na který chcete přepnout (bude další) (W (winter) - S (summer))",
                choices=["W", "S"],
                required=True
            )
    ) -> None:
        # TODO: test what happens if someone calls this without ADMIN perms

        for category in ctx.guild.categories:
            category_name = category.name.split()
            if len(category_name[0]) == 2 and category_name[1] == "semestr":
                self.switch_categories(category)

        await ctx.respond("Channels switched!", ephemeral=True)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(SemesterSwitching(bot))
