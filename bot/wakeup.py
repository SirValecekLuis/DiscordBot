import asyncio
import discord
from discord.ext import commands


class WakeUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="wakeup", description="Ping a user multiple times and delete the messages."
    )
    @commands.cooldown(2, 86400)  # Allow 2 uses per day (86400 seconds in a day)
    async def wakeup(self, ctx, user: discord.User):
        if ctx.command.get_cooldown_retry_after(ctx) > 0:
            await ctx.respond(
                f"Máš cooldown. Prosím počkej {ctx.command.get_cooldown_retry_after(ctx)/3600:.2f} hod před použitím příkazu znovu.",
                ephemeral=True,
            )
            return
        # loops
        loops = 3
        loop_delay = 2

        # Define the number of pings in a row in 1 loop
        num_pings = 5  # Going for more results in getting blocked by Discord anti-spam

        # Reply so Discord doesn't throw an error
        await ctx.respond("Začínám pingovat", ephemeral=True)

        for i in range(loops):
            # Mention the user multiple times and send the messages
            ping_messages = []
            for _ in range(num_pings):
                await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
                ping_messages.append(await ctx.send(f"{user.mention}"))
            # Delete the ping messages
            for message in ping_messages:
                await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
                await message.delete()
            if i != loops - 1:
                await asyncio.sleep(loop_delay)

        await ctx.respond("Končím s pingováním", ephemeral=True)


def setup(bot):
    bot.add_cog(WakeUp(bot))
