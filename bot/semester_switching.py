"""This module is for semester switching, wow."""
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
        channel name is in this way: "x. semestr" or "x. semestr - archiv" and only 0-9 is supported right now.
        discord roles will follow the same pattern as "EMOJI NUMBER NAME" such as "1️⃣ Prvák" and will not be changed.
        """
        # TODO: test what happens if someone calls this without ADMIN perms
        # TODO: add some level of stupid proofing (maybe some kind of acceptance from others or something like that)
        try:
            await ctx.send("Please, bear in mind this command may take several minutes due to discord API calls.",
                           delete_after=True)
            await ctx.defer(ephemeral=True)  # Discord API takes way too long to respond

            # This is just for error purposes
            visited_categories = []
            for category in ctx.guild.categories:
                print(category)
                category_name = category.name.split()
                if len(category_name[0]) == 2 and category_name[1] == "semestr" and len(category_name) == 2:
                    # Semester is active and should be put as archived

                    """
                    Adds - archive to a category name
                    Removes role (prvák, druhák...)
                    Disallows public/private threads, send messages in them and sending messages overall for everyone
                    Resets View Channel for everyone to its default state
                    """
                    new_overwrites = category.overwrites
                    for role_name, overwrite in category.overwrites.items():
                        year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year
                        if role_name.name == ROLES[year]:
                            role_to_remove = discord.utils.get(category.guild.roles, name=ROLES[year])
                            new_overwrites = {role: overwrite for role, overwrite in category.overwrites.items() if
                                              role != role_to_remove}
                    new_overwrites[category.guild.default_role] = discord.PermissionOverwrite(
                        create_public_threads=False,
                        create_private_threads=False,
                        send_messages_in_threads=False,
                        send_messages=False,
                        view_channel=None
                    )

                    # Name of channel
                    name = category.name + " - archiv"
                    print("archived")
                    print(name)

                    # Final edit of category
                    visited_categories.append(category)
                    await category.edit(name=name, overwrites=new_overwrites)
                elif len(category_name[0]) == 2 and category_name[1] == "semestr" and category_name[3] == "archiv":
                    # Semester is archived and should be put as active

                    """
                    Removes - archive from name
                    Adds role (prvák, druhák...) and enables View Channel for the role
                    Disallows view channel for everyone
                    Allows Send Messages, Send Messages in Threads and Create Private/Public threads for everyone
                    """
                    new_overwrites = category.overwrites
                    year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year
                    role_to_add = discord.utils.get(category.guild.roles, name=ROLES[year])
                    new_overwrites[role_to_add] = discord.PermissionOverwrite(view_channel=True)
                    new_overwrites[category.guild.default_role] = discord.PermissionOverwrite(
                        view_channel=False,
                        create_public_threads=True,
                        create_private_threads=True,
                        send_messages_in_threads=True,
                        send_messages=True
                    )

                    # Name of channel
                    name = category_name[0] + " " + category_name[1]
                    print("active")
                    print(name)

                    # Final edit of category
                    visited_categories.append(category)
                    await category.edit(name=name, overwrites=new_overwrites)

            await ctx.followup.send("Channels switched!", ephemeral=True)
        except discord.HTTPException as e:
            text = " | ".join([category.name for category in visited_categories])
            raise Exception("semester_switching failed. 15m API response was not enough. In this case, unfortunately,"
                            "we have no idea what was executed and what was not. Therefore there is a list of"
                            "categories that have been/could have been changed with error attached." + text + e)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(SemesterSwitching(bot))
