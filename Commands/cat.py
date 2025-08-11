import discord
from discord.ext import commands
import os

FORBIDDEN_FILES = [
    ".env",
    "LICENSE",
    "__pycache__",
    ".gitignore",
    "Tux",
    "dev.nix",
    "..",
    ".log",
    ".json"
]

class main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    async def cat(self, ctx, filedestination: str):
        if any(forbidden in filedestination for forbidden in FORBIDDEN_FILES):
            await ctx.send("You cannot request that file!")
            return
        try:
            attachment = discord.File(filename=filedestination, fp=filedestination)
            await ctx.send(file=attachment)
        except IsADirectoryError:
            await ctx.send("Error: File is a directory.")
        except FileNotFoundError:
            await ctx.send(f"Error: File not found at `{filedestination}`.")

async def setup(bot):
    await bot.add_cog(main(bot))
    print("CAT cog loaded.")