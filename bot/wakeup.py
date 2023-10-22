import asyncio
import discord
from discord.ext import commands

class WakeUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="wakeup",
        description="Ping a user multiple times and delete the messages."
    )
    async def wakeup(self, ctx, user: discord.User):
        # loops
        loops = 3
        loop_delay = 2

        # Define the number of pings in a row in 1 loop
        num_pings = 5 # going for more results in getting blocked by discord anti-spam, hence the loop mechanism - even more annoying

        # Reply so discord doesn't throw an error
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
            if (i != loops-1):
                await asyncio.sleep(loop_delay)

        await ctx.respond("Končím s pingováním", ephemeral=True)
        

        

def setup(bot):
    bot.add_cog(WakeUp(bot))
