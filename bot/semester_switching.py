"""This module is for semester switching, wow."""
import discord
from discord.ext import commands
import math

from error_handling import send_error_message_to_user

ROLES = {1: "1️⃣ Prvák", 2: "2️⃣ Druhák", 3: "3️⃣ Třeťák", 4: "4️⃣ Čtvrťák", 5: "5️⃣ Páťák"}


class SemesterSwitching(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    async def switch_to_archived(self, category: discord.CategoryChannel, category_name: list,
                                 visited_categories: list) -> None:
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

        # Final edit of category
        visited_categories.append(category)
        await category.edit(name=name, overwrites=new_overwrites)

        # sync perms after editing category
        for channel in category.channels:
            await channel.edit(sync_permissions=True)

    async def switch_to_active(self, category: discord.CategoryChannel, category_name: list,
                               visited_categories: list) -> None:
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

        # Final edit of category
        visited_categories.append(category)
        await category.edit(name=name, overwrites=new_overwrites)

        # sync perms after editing category
        for channel in category.channels:
            await channel.edit(sync_permissions=True)

    @commands.slash_command(name='switch-semester',
                            description='Tento příkaz přehází semestry do správných kategorii pro nový semestr.')
    @commands.has_permissions(administrator=True)
    async def switch_semester(self, ctx: discord.ApplicationContext) -> None:
        """
        PREREQUISITES
        Channel name is in this way: "x. semestr" or "x. semestr - archiv" and only 0-9 is supported right now.
        Discord role ID will be inserted in DB with name x_year_role_id with value of ID (int) of given role.
        (Can be obtained via discord when activating developer mode and then right-clicking on role)
        """
        # TODO: add some level of stupid proofing (maybe some kind of acceptance from others or something like that)

        # This is just for error purposes
        visited_categories = []
        try:
            await ctx.defer(ephemeral=True)  # Discord API takes way too long to respond
            await ctx.followup.send("Tento příkaz může trvat několik minut kvůli API callům. Zpracovávám...")

            for category in ctx.guild.categories:
                category_name = category.name.split()

                # Semester is active and should be put as archived
                if len(category_name[0]) == 2 and category_name[1] == "semestr" and len(category_name) == 2:
                    await self.switch_to_archived(category, category_name, visited_categories)

                # Semester is archived and should be put as active
                elif len(category_name[0]) == 2 and category_name[1] == "semestr" and category_name[3] == "archiv":
                    await self.switch_to_active(category, category_name, visited_categories)

            await ctx.followup.send("Prohození semestrů bylo dokončeno!", ephemeral=True)
        except discord.HTTPException as e:
            text = " | ".join([category.name for category in visited_categories])
            if len(visited_categories) == 0:
                text = "NO CHANNELS"
            raise Exception("API neodpovědělo do 15 minut. Channely, které mohly být ovlivněny, jsou vypsány společně s"
                            "chybovou hláškou, která stála za pád tohoto commandu." + text + str(e))
        except Exception as e:
            text = " | ".join([category.name for category in visited_categories])
            raise Exception(
                "Něco selhalo. Teoreticky ovlivněné kategorie + chybová hláška bude vypsána." + text + str(e))

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(SemesterSwitching(bot))
