import discord
from discord.ext import commands
from datetime import datetime
import os, json

class postwall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        
        if current_server_id not in data:
            data[current_server_id] = {
                "ann_channel": 0 
            }

        if "ann_channel" not in data[current_server_id]:
            data[current_server_id]["ann_channel"] = 0
        
        return data

    @commands.command()
    async def wall(self, ctx, *, arg: str=None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have sudo privileges to execute this command.")
            return

        if arg is None:
            await ctx.send("Invalid arguments. Use `wall <message>`")
        
        csi = str(ctx.guild.id)
        data = self.read(csi)

        if data[csi]["ann_channel"] == 0:
            return

        ch = discord.utils.get(ctx.guild.text_channels, id=data[csi]["ann_channel"])
        cur_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        await ch.send(f"""```
        Broadcast message from root@{ctx.author.name} ({cur_time}):
        
        {arg}```""")

async def setup(bot):
    await bot.add_cog(postwall(bot))