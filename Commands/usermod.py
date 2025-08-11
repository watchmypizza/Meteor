import discord
from discord.ext import commands

class usercmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def usermod(self, ctx, arg: str, newuser: str, olduser: discord.Member):
        if not ctx.author.guild_permissions.moderate_members:
            await ctx.send("You do not have permission to use this command!")
            return

        if arg != "-l":
            await ctx.send("Usage: `usermod -l <new_nickname> <user>`")
            return

        if not newuser:
             await ctx.send("Usage: `usermod -l <new_nickname> <user>`")
             return

        try:
            await olduser.edit(nick=newuser)
            await ctx.send(f"Successfully changed {olduser.display_name}'s nickname to `{newuser}`.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change that user's nickname.")
        except Exception as e:
            await ctx.send(f"An error occurred while changing the nickname: {e}")


async def setup(bot):
    await bot.add_cog(usercmd(bot))