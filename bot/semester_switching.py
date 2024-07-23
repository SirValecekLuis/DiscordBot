"""This module is for semester switching, wow."""

import asyncio
import math

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user
from start import db


async def switch_to_active(category: discord.CategoryChannel, category_name: list, visited_categories: list) -> None:
    """
    Removes - archive from name
    Adds a role (prvák, druhák...) and enables View Channel for the role
    Disallows view channel for everyone
    Allows To Send Messages, Send Messages in Threads and Create Private/Public threads for everyone
    """
    # role_id of the given semester category
    year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year || 0-9 only
    role_to_search = f"{year}_year_role_id"
    role_id = await db.get_variable_from_variables(role_to_search)
    if role_id is None:
        raise Exception(f"Role s daným názvem {role_to_search} nebyla nalezena v DB.")

    new_overwrites = category.overwrites
    role_to_add = discord.utils.get(category.guild.roles, id=role_id)
    new_overwrites[role_to_add] = discord.PermissionOverwrite(view_channel=True)
    new_overwrites[category.guild.default_role] = discord.PermissionOverwrite(
        view_channel=False,
        create_public_threads=True,
        create_private_threads=True,
        send_messages_in_threads=True,
        send_messages=True,
    )

    # Name of a channel
    name = category_name[0] + " " + category_name[1]

    # Final edit of category
    visited_categories.append(category)
    await category.edit(name=name, overwrites=new_overwrites)

    # sync perms after editing category
    for channel in category.channels:
        await channel.edit(sync_permissions=True)


async def switch_to_archived(category: discord.CategoryChannel, category_name: list, visited_categories: list) -> None:
    """
    Adds - archive to a category name
    Removes a role (prvák, druhák...)
    Disallows public/private threads, send messages in them and sending messages overall for everyone
    Resets View Channel for everyone to its default state
    """
    # role_id of the given semester category
    year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year
    role_to_search = f"{year}_year_role_id"
    role_id = await db.get_variable_from_variables(role_to_search)
    if role_id is None:
        raise Exception(f"Role s daným názvem {role_to_search} nebyla nalezena v DB.")
    role_from_db = category.guild.get_role(role_id)

    # Find and remove a role from given category
    new_overwrites = category.overwrites
    for role, overwrite in category.overwrites.items():
        if role.id == role_from_db.id:
            new_overwrites = {role: overwrite for role, overwrite in category.overwrites.items() if
                              role != role_from_db}
            break

    # Change permissions of given category
    new_overwrites[category.guild.default_role] = discord.PermissionOverwrite(
        create_public_threads=False,
        create_private_threads=False,
        send_messages_in_threads=False,
        send_messages=False,
        view_channel=None,
    )

    # Name of a channel
    name = category.name + " - archiv"

    # Final edit of category
    visited_categories.append(category)
    await category.edit(name=name, overwrites=new_overwrites)

    # sync perms after editing category
    for channel in category.channels:
        await channel.edit(sync_permissions=True)


async def sort_categories(ctx: discord.ApplicationContext) -> None:
    """
    This function will sort categories, so the active one will be above voice channels, and archived will be under.
    :param ctx: Context of slash command
    :return: None
    """
    try:
        categories = ctx.guild.categories

        # list of categories (divided on active and archived)
        archived_categories = [category for category in categories
                               if len(category.name.split()) == 4 and category.name.split()[3] == "archiv"]
        active_categories = [category for category in categories
                             if len(category.name.split()) == 2 and category.name.split()[1] == "semestr"]

        # If semester categories were empty
        if len(archived_categories) == 0 and len(active_categories) == 0:
            await ctx.followup.send("Příkaz byl proveden, ale nebyly nalezeny žádné kategorie, které by byly změněny.")
            return

        # sorted by ascending order by first number (x. semestr)
        archived_categories.sort(key=lambda category: int(category.name[0]), reverse=True)
        active_categories.sort(key=lambda category: int(category.name[0]), reverse=True)

        # get id to get a channel
        voice_category_id = await db.get_variable_from_variables("voice_category_id")
        if voice_category_id is None:
            raise Exception("voice_category_id nebylo nastaveno do databáze.")

        # get channel
        voice_category = ctx.guild.get_channel(voice_category_id)
        if voice_category is None:
            raise Exception("voice category nebyla nalezena se zadaným ID.")

        # Discord indexes from 0
        voice_category_pos = voice_category.position

        # Only god and I knew how this works, now only god knows

        # I take all categories before voice category and remove semester categories
        first_half = categories[:voice_category_pos]
        first_half = [item for item in first_half if item not in archived_categories and item not in active_categories]

        # The second half is after voice category, the same logic
        second_half = categories[voice_category_pos:]
        second_half = [item for item in second_half if
                       item not in archived_categories and item not in active_categories]

        # Removed voice category from the second half as it is included and I want to add it manually later myself
        second_half.remove(voice_category)

        # In this part, I will put the categories in order I would like to have them
        # First, I take categories that are before semester categories
        sorted_categories = []
        index = 0
        for category in first_half:
            sorted_categories.append((category, index))
            index += 1

        # Then, I will insert semester categories
        for category in active_categories:
            sorted_categories.append((category, index))
            index += 1

        # Now the voice category itself
        sorted_categories.append((voice_category, index))
        index += 1

        # Now archived semester categories after voice category
        for category in archived_categories:
            sorted_categories.append((category, index))
            index += 1

        # And the rest of categories at the end
        for category in second_half:
            sorted_categories.append((category, index))
            index += 1

        # Final API position change of all categories
        for category, index in sorted_categories:
            await category.edit(position=index)

    except discord.HTTPException as e:
        raise Exception("Http error z discord API, error: " + str(e)) from e
    except Exception as e:
        raise Exception("Něco nastalo špatně během seřazování kategorii. " + str(e)) from None


async def warn_user(ctx: discord.ApplicationContext) -> bool:
    """This function will create a message with buttons to warn an administrator before using this command accidentally.
    :param ctx: Slash command context
    :return: True if command was accepted by administrator and False if declined
    """
    # Create an Event to signal when a button is pressed
    event = asyncio.Event()

    # default False if anything fails, we do not want to accept the command
    accepted = False

    # Button creation
    accept_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Přijmout")
    decline_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Odmítnout")

    # Callbacks
    async def accept_callback(interaction: discord.Interaction) -> None:    # pylint: disable=unused-argument
        """It is called when a user accepts the command via green button.
        :return: None
        """
        nonlocal accepted, message
        accepted = True

        event.set()

    async def decline_callback(interaction: discord.Interaction) -> None:   # pylint: disable=unused-argument
        """It is called when a user declines the command via red button.
        :param interaction: Interaction with button from user
        :return: None
        """
        nonlocal accepted, message
        accepted = False

        event.set()

    accept_button.callback = accept_callback
    decline_button.callback = decline_callback

    # View with buttons
    view = discord.ui.View(timeout=30)  # 30 second time wait
    view.add_item(accept_button)
    view.add_item(decline_button)

    # Final message
    message: discord.Message | None = await ctx.followup.send(
        "VAROVÁNÍ: Tento příkaz prohodí všechny semestry a přehází jejich role, "
        "prosím, ujistěte se, že je nastaveno ID pro voice category a ID všech rolí studentů.",
        view=view,
    )

    # Wait for the event to be set or for the timeout
    try:
        await asyncio.wait_for(event.wait(), timeout=30)
    except asyncio.TimeoutError:
        await ctx.followup.send("Čas vypršel. Operace zrušena.", ephemeral=True)
        await message.delete()
        return False

    if message is not None:
        await message.edit(content="Příkaz byl úspěšně přijat! Příkaz může trvat několik minut kvůli API callům. "
                                   "Provádím...", view=None)

    return accepted


class SemesterSwitching(commands.Cog):
    """This class represents a cog that will handle semester switching."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="switch-semester",
        description="Tento příkaz přehází semestry do správných kategorii pro nový semestr.",
    )
    @commands.has_permissions(administrator=True)
    async def switch_semester(self, ctx: discord.ApplicationContext) -> None:
        """PREREQUISITES
        Channel name is in this way: "x. semestr" or "x. semestr - archiv" and only 0-9 is supported right now.
        Discord role ID will be inserted in DB with name x_year_role_id with value of ID (int) of a given role.
        Discord voice channel category ID will be inserted in DB with name voice_category_id.
        (Can be obtained via discord when activating developer mode and then right-clicking on a role)
        """
        # This is just for error purposes
        visited_categories = []
        try:
            # Discord API takes way too long to respond
            await ctx.defer(ephemeral=True)

            # Warn admin before using this command
            if await warn_user(ctx) is False:
                return

            # Go through all the categories
            for category in ctx.guild.categories:
                category_name = category.name.split()

                # The Semester is active and should be put as archived
                if len(category_name[0]) == 2 and category_name[1] == "semestr" and len(category_name) == 2:
                    await switch_to_archived(category, category_name, visited_categories)

                # The Semester is archived and should be put as active
                elif len(category_name[0]) == 2 and category_name[1] == "semestr" and category_name[3] == "archiv":
                    await switch_to_active(category, category_name, visited_categories)

            # Sort categories, called after all names, perms and roles were switched
            await sort_categories(ctx)

            await ctx.followup.send("Prohození semestrů bylo dokončeno!", ephemeral=True)
        except discord.HTTPException as e:
            text = " | ".join([category.name for category in visited_categories])
            if len(visited_categories) == 0:
                text = "NO CATEGORIES"
            raise Exception(
                "API neodpovědělo do 15 minut. Channely, které mohly být ovlivněny, jsou vypsány společně s"
                "chybovou hláškou, která stála za pád tohoto commandu. " + text + " " + str(e),
            ) from e
        except Exception as e:
            text = " | ".join([category.name for category in visited_categories])
            raise Exception(
                "Něco selhalo. Teoreticky ovlivněné kategorie + chybová hláška bude vypsána. KATEGORIE: "
                + text
                + " ERROR: "
                + str(e),
            ) from e

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
    bot.add_cog(SemesterSwitching(bot))
