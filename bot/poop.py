import random
import discord
from discord.ext import commands

class Poop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="poop",
        description="💩"
    )
    async def poop(self, ctx):
         # List of words to choose from
        words = ["apps", "poli", "osu", "kudělka", "dvorský", "fpr"]

        # Select a random word from the list
        random_word = random.choice(words)
        # Define the ASCII art
        ascii_art = f"""
        ⠀⠀⢀⣤⣶⣶⣤⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⡄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⡿⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀
⠀⠀⠀⠀⢠⣿⣿⣿⣿⡿⣿⣿⣧⣀⠀⠀
⠀⠀⠀⠀⢺⣿⣿⣿⣿⣧⣬⣻⢿⣿⣿⡦
⠀⠀⠀⠀⠀⠙⠻⠿⢿⣿⣿⣿⣿⡏⠛⠁
⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⣽⣿⡿⠁⠀⠀
⠀⢀⡠⣿⣷⣤⡀⠀⠀⢸⣿⣿⠃⠀⠀⠀
⠰⠿{random_word}⠿⠇⠀⠠⠿⠿⠏⠀
        """

        # Create an embedded message with a specific color
        embed = discord.Embed(
            title=":poop:",
            description=f"```\n{ascii_art}\n```",
            color=0xFF5733  # Change the color here (use a decimal representation of the color)
        )
        
        # Send the embedded message
        await ctx.send(embed=embed)

        # Reply so discord doesn't throw an error
        await ctx.respond("Vykakáno", ephemeral=True)

def setup(bot):
    bot.add_cog(Poop(bot))
