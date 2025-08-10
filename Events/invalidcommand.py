import discord
from discord.ext import commands
import os

class commanderrorhandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
                return
        print(f"Command: {ctx.command}, Error: {error}")
        try:
            with open("errors.log", "a") as f:
                f.write(f"Command: {ctx.command}, Error: {error}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
        

async def setup(bot):
    await bot.add_cog(commanderrorhandler(bot))
    print("Error Handler event cog loaded.")