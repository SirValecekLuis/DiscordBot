"""This module is for semester switching, wow."""
import discord
from discord.ext import commands
import math

from error_handling import send_error_message_to_user
from start import db


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

        # role_id of the given semester category
        year = math.ceil(int(category_name[0][0]) / 2)  # [1]. semestr = 1/2 = ceil(0.5) = 1. year
        role_to_search = f"{year}_year_role_id"
        role_id = await db.get_variable_from_variables(role_to_search)
        if role_id is None:
            raise Exception(f"Role s daným názvem {role_to_search} nebyla nalezena v DB.")
        role_from_db = category.guild.get_role(role_id)

        new_overwrites = category.overwrites
        for role, overwrite in category.overwrites.items():
            if role.name == role_from_db.name:
                role_to_remove = discord.utils.get(category.guild.roles, id=role_id)
                new_overwrites = {role: overwrite for role, overwrite in category.overwrites.items() if
                                  role != role_to_remove}
                break

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

    async def sort_categories(self, ctx: discord.ApplicationContext) -> None:
        """
        This function will sort categories so the active one will be above voice channels and archived will be under.

        :param ctx:
        :return: None
        """

        try:
            categories = ctx.guild.categories

            # list of categories (divided on active and archived)
            archived_categories = [category for category in categories if
                                   len(category.name.split()) == 4 and category.name.split()[3] == "archiv"]
            active_categories = [category for category in categories if
                                 len(category.name.split()) == 2 and category.name.split()[1] == "semestr"]

            # If semester categories were empty
            if len(archived_categories) == 0 and len(active_categories) == 0:
                await ctx.followup.send(
                    "Příkaz byl proveden, ale nebyly nalezeny žádné kategorie, které by byly změněny.")
                return

            # sorted by ascending order by first number (x. semestr)
            archived_categories.sort(key=lambda category: int(category.name[0]), reverse=True)
            active_categories.sort(key=lambda category: int(category.name[0]), reverse=True)

            # get id to get channel
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
            first_half = [item for item in first_half if
                          item not in archived_categories and item not in active_categories]
            # The second half is after voice category, the same logic
            second_half = categories[voice_category_pos:]
            second_half = [item for item in second_half if
                           item not in archived_categories and item not in active_categories]
            # Removed voice category from second half as it is included and I want to add it manually later myself
            second_half.remove(voice_category)

            # In this part I will put the categories in order I would like to have them
            # First, I take channels that are before semester categories
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

        except Exception as e:
            raise Exception("Něco nastalo špatně během seřazování kategorii. " + str(e))
        except discord.HTTPException as e:
            raise Exception("Http error z discord API, error: " + str(e))

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

            # Sort categories, called after all categories are sorted and their perms are changed
            await self.sort_categories(ctx)

            await ctx.followup.send("Prohození semestrů bylo dokončeno!", ephemeral=True)
        except discord.HTTPException as e:
            text = " | ".join([category.name for category in visited_categories])
            if len(visited_categories) == 0:
                text = "NO CATEGORIES"
            raise Exception("API neodpovědělo do 15 minut. Channely, které mohly být ovlivněny, jsou vypsány společně s"
                            "chybovou hláškou, která stála za pád tohoto commandu. " + text + " " + str(e))
        except Exception as e:
            text = " | ".join([category.name for category in visited_categories])
            raise Exception(
                "Něco selhalo. Teoreticky ovlivněné kategorie + chybová hláška bude vypsána. KATEGORIE: "
                + text + " ERROR: " + str(e))

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(SemesterSwitching(bot))
