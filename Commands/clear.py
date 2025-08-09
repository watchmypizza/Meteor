import discord
from discord.ext import commands

class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def clear(self, ctx, amt: int = None):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have sudo privileges to execute this command.")
            return

        if amt is None:
            await ctx.send("Invalid arguments. Use `clear <amount>`")
            return

        limit = amt

        try:
            deleted = await ctx.channel.purge(limit=limit, before=ctx.message)

            cleared_count = len(deleted)

            if cleared_count == 0:
                await ctx.send("No messages cleared.")
            elif cleared_count == 1:
                await ctx.send("Cleared `1` message.")
            else:
                await ctx.send(f"Cleared `{cleared_count}` messages.")

        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to delete messages.")
        except discord.HTTPException as e:
            await ctx.send(f'An error occurred: {e}')


async def setup(bot):
    print("Clear cog loaded.")
    await bot.add_cog(clear(bot))