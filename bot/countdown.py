"""This is a module that will handle exam countdowns and send them to channels."""

from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands, tasks


class CountDown(commands.Cog):
    """This class is for showing time that remains till some exam."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.message_to_delete = None
        self.started = False
        self.ctx = None

    @tasks.loop(hours=12, minutes=1, seconds=1)
    async def start_countdown_called(self) -> None:
        """
        Function that handles sending messages with time remaining and repeats itself after x hours.
        :return: None
        """
        if self.message_to_delete is not None:
            await self.message_to_delete.delete()

        # Test 1164923191542693920
        # Ofiko 1078965904093745252
        channel = self.bot.get_channel(1078965904093745252)  # Hardcoded variable is the best variable
        time_now_utc = datetime.now(timezone.utc)

        cet = timezone(timedelta(hours=1))
        cest = timezone(timedelta(hours=2))

        def is_dst(dt: datetime) -> bool:
            """
            Returns if dst.
            :param dt: Datetime
            :return: Bool
            """
            return bool(dt.dst())

        prague_tz = cest if not is_dst(time_now_utc.astimezone(cest)) else cet

        time_exam = datetime(2024, 6, 12, 8, 0, tzinfo=prague_tz)
        time_diff = time_exam - time_now_utc.astimezone(prague_tz)

        if time_diff.total_seconds() < 0:
            return

        total_seconds = int(time_diff.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        def pluralize(value, singular, plural):
            return singular if value == 1 else plural

        hours_str = pluralize(hours, "hodinu", "hodiny" if hours in [2, 3, 4] else "hodin")
        minutes_str = pluralize(minutes, "minutu", "minuty" if minutes in [2, 3, 4] else "minut")
        seconds_str = pluralize(seconds, "sekundu", "sekundy" if seconds in [2, 3, 4] else "sekund")

        guild = self.ctx.guild
        emoji = discord.utils.get(guild.emojis, name="olivkacursed")

        self.message_to_delete = await channel.send(
            f"***Tvá smrt v podobě zkoušky z APPS přichází za "
            f"{hours} {hours_str} {minutes} {minutes_str} a {seconds} {seconds_str}.*** {emoji}\n"
            f"*||Zlé hlasy říkají, že úspěšnost je 50%. :skull:||*")

    @commands.slash_command(name='start-countdown')
    async def start_countdown(self, ctx: discord.ApplicationContext) -> None:
        """
        The slash command that activates the countdown in a given channel.
        :param ctx: Slash command context
        :return: None
        """
        if self.started:
            await ctx.respond("Odpočet už běží.", ephemeral=True)
            return

        self.started = True
        self.ctx = ctx
        await ctx.respond("Odpočet byl započat.", ephemeral=True)
        self.start_countdown_called.start()


def setup(bot: discord.Bot) -> None:
    """This is just a setup for start.py"""
    bot.add_cog(CountDown(bot))
