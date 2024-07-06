"""This module is for semestr switching, wow."""
import discord
from discord.ext import commands
import math

from error_handling import send_error_message_to_user

ROLES = {1: "1️⃣ Prvák", 2: "2️⃣ Druhák", 3: "3️⃣ Třeťák", 4: "4️⃣ Čtvrťák", 5: "5️⃣ Páťák"}


class SemesterSwitching(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name='switch-semester',
                            description='Tento příkaz přehází semestry do správných kategorii pro nový semestr.')
    @commands.has_permissions(administrator=True)
    async def switch_semester(self, ctx: discord.ApplicationContext) -> None:
        """
        PREREQUISITES
        channel name is in this way: "x. semestr" or "x. semestr - archiv"
        discord roles will follow the same pattern as "EMOJI NUMBER NAME" such as "1️⃣ Prvák" and will not be changed
        """
        # TODO: test what happens if someone calls this without ADMIN perms
        try:
            await ctx.defer(ephemeral=True)  # Discord API takes way too long to respond

            for category in ctx.guild.categories:
                category_name = category.name.split()
                if len(category_name[0]) == 2 and category_name[1] == "semestr" and len(category_name) == 2:
                    # Semester is active and should be put as archive

                    # Removes role (prvák, druhák...)
                    new_overwrites = category.overwrites
                    for role_name, overwrite in category.overwrites.items():
                        year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year
                        if role_name.name == ROLES[year]:
                            role_to_remove = discord.utils.get(category.guild.roles, name=ROLES[year])
                            new_overwrites = {role: overwrite for role, overwrite in category.overwrites.items() if
                                              role != role_to_remove}

                    # Name of channel
                    name = category.name + " - archiv"
                    print("archived")
                    print(name)

                    # Final edit of category
                    await category.edit(name=name, overwrites=new_overwrites)
                elif len(category_name[0]) == 2 and category_name[1] == "semestr" and len(category_name) > 2:
                    # Semester is archived and should be put as active

                    # Name of channel
                    name = category_name[0] + " " + category_name[1]
                    print("active")
                    print(name)

                    # Final edit of category
                    await category.edit(name=name)

            await ctx.followup.send("Channels switched!", ephemeral=True)
        except discord.HTTPException as e:
            raise Exception("semester_switching failed. 15m API response was not enough." + e)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(SemesterSwitching(bot))
