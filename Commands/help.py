import discord
from discord.ext import commands

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Help",
            description="Please use the `$ man <command>` feature instead.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help(bot))