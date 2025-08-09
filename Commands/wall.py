import discord
from discord.ext import commands
from datetime import datetime

class postwall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def wall(self, ctx, *, arg: str=None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have sudo privileges to execute this command.")
            return

        if arg is None:
            await ctx.send("Invalid arguments. Use `wall <message>`")
        
        ch = discord.utils.get(ctx.guild.text_channels, id=1392619508283347177)
        cur_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        await ch.send(f"""```
        Broadcast message from root@{ctx.author.name} ({cur_time}):
        
        {arg}```""")

async def setup(bot):
    await bot.add_cog(postwall(bot))
    print("WALL cog loaded.")