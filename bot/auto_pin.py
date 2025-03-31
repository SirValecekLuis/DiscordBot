"""Cog that pins a message after a certain threshold of
specific reactions is reached.
"""

from typing import Union

import discord
from discord.ext import commands

from error_handling import send_error_message_to_user


class AutoPin(commands.Cog):
    """This class serves as a Cog that handles auto pinning."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.pin_emoji = "📌"
        self.pin_threshold = 5

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
        """Pins a message if a certain threshold of reactions
        has been reached
        """
        message = reaction.message

        if message.pinned:
            return

        yes_count = 0

        for message_reaction in [x for x in message.reactions if x.emoji == self.pin_emoji]:
            yes_count += message_reaction.count

        # if an error occurs, it should be handled by cog_command_error
        if yes_count >= self.pin_threshold:
            try:
                await message.pin()
            except discord.HTTPException as e:
                raise Exception(
                    f"Pin limit pro channel {message.channel} byl dosažen."
                    f"Uživatel, který chtěl pinnout: {user.jump_url}"
                    f"Zpráva k pinnutí: {message.jump_url}",
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
    bot.add_cog(AutoPin(bot))
