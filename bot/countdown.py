import discord
from datetime import datetime, timezone, timedelta
from discord.ext import commands, tasks


class CountDown(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.message_to_delete = None
        self.started = False
        self.ctx = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        pass

    @tasks.loop(hours=1)
    async def start_countdown_called(self):
        if self.message_to_delete is not None:
            await self.message_to_delete.delete()

        channel = self.bot.get_channel(1078965904093745252)  # Hardcoded variable is the best variable
        time_now_utc = datetime.now(timezone.utc)

        cet = timezone(timedelta(hours=1))
        cest = timezone(timedelta(hours=2))

        is_dst = lambda dt: bool(dt.dst())

        prague_tz = cest if not is_dst(time_now_utc.astimezone(cest)) else cet

        time_now = time_now_utc.astimezone(prague_tz)
        time_exam = datetime(2024, 5, 30, 8, 0, tzinfo=prague_tz)
        time_diff = time_exam - time_now
        time_diff = round(time_diff.total_seconds() / 3600)

        if time_diff < 0:
            return

        guild = self.ctx.guild
        emoji = discord.utils.get(guild.emojis, name="olivkacursed")

        self.message_to_delete = await channel.send(f"*Čas do zkoušky zbývá: {time_diff} hodin.* {emoji}")

    @commands.slash_command(name='start_countdown')
    async def start_countdown(self, ctx: discord.ApplicationContext):
        if self.started:
            await ctx.respond("Odpočet už běží.", ephemeral=True)
            return

        self.started = True
        self.ctx = ctx
        await ctx.respond("Odpočet byl započat.", ephemeral=True)
        self.start_countdown_called.start()


def setup(bot: discord.Bot) -> None:
    bot.add_cog(CountDown(bot))
