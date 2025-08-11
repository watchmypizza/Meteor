import discord
from discord.ext import commands
import os

class pwdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pwd(self, ctx):
        current_path = os.getcwd()
        await ctx.send(f"{current_path}")

async def setup(bot):
    await bot.add_cog(pwdCog(bot))