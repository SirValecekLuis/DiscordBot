import discord
import asyncio
from datetime import datetime
from discord.ext import commands


class CountDown(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.message_to_delete = None
        self.started = False

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        pass

    @commands.slash_command(name='start_countdown')
    async def start_countdown(self, ctx: discord.ApplicationContext):
        if self.started:
            await ctx.respond("Odpočet už běží.", ephemeral=True)
            return

        self.started = True

        while True:
            if self.message_to_delete is not None:
                await self.message_to_delete.delete()

            channel = self.bot.get_channel(1078965904093745252)  # Hardcoded variable is the best variable
            time_now = datetime.now()
            time_exam = datetime(2024, 5, 30, 8, 0)
            time_diff = time_exam - time_now
            time_diff = round(time_diff.total_seconds() / 3600)

            if time_diff < 0:
                return

            guild = ctx.guild
            emoji = discord.utils.get(guild.emojis, name="olivkacursed")

            self.message_to_delete = await channel.send(f"*Čas do zkoušky zbývá: {time_diff} hodin.* {emoji}")
            await ctx.respond("Odpočet byl započat.", ephemeral=True)
            await asyncio.sleep(3600)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(CountDown(bot))
