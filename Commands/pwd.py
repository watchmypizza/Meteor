import discord
from discord.ext import commands
import os

class pwdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pwd(self, ctx):
        await ctx.send(f"/home/Meteor/")

async def setup(bot):
    await bot.add_cog(pwdCog(bot))