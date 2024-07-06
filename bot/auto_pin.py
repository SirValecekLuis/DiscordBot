"""Cog that pins a message after a certain threshold of
   specific reactions is reached."""
import discord
from discord.ext import commands

from typing import Union

from error_handling import send_error_message_to_user


class AutoPin(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.pin_emoji = '📌'
        self.pin_threshold = 5
        self.unpin_threshold = 2

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,
                              user: Union[discord.Member,
                                          discord.User]) -> None:
        """Pins a message if a certain threshold of reactions
           has been reached"""
        message = reaction.message

        if message.pinned:
            return

        yes_count = 0

        for reaction in [x for x in message.reactions
                         if x.emoji == self.pin_emoji]:
            yes_count += reaction.count

        # if error occurs, it should be handled by cog_command_error
        if yes_count >= self.pin_threshold:
            try:
                await message.pin()
            except discord.HTTPException:
                raise Exception(f"Pin limit for a channel {message.channel} has been reached."
                                f"User trying to pin: {user.jump_url}"
                                f"Message: {message.jump_url}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction,
                                 user: Union[discord.Member,
                                             discord.User]) -> None:
        """Unpins a message if a certain threshold of reactions
           is no longer being reached"""
        message = reaction.message

        if not message.pinned:
            return

        yes_count = 0

        for reaction in [x for x in message.reactions
                         if x.emoji == self.pin_emoji]:
            yes_count += reaction.count

        if yes_count <= self.unpin_threshold:
            await message.unpin()


    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError) -> None:
        await send_error_message_to_user(ctx, error)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AutoPin(bot))
