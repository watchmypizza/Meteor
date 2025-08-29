import discord
from discord.ext import commands
from discord import app_commands
import os, json

class goodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.json) or os.path.getsize(self.json) == 0:
            data = {}
        else:
            with open(self.json, "r") as f:
                data = json.load(f)
        
        if current_server_id not in data:
            data[current_server_id] = {
                "logging_channel": 0,
                "welcomer_channel": 0
            }
        
        return data
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        csi = str(member.guild.id)
        if csi is None:
            return
        data = self.read(csi)
        if data[csi]["welcomer_channel"] == 0:
            return
        channel = discord.utils.get(member.guild.channels, id=data[csi]["welcomer_channel"])
        embed = discord.Embed(
            title="Goodbye!",
            description="Goodbye {}, we hope to see you again!".format(member.mention),
            color=discord.Color.red()
        )
        embed.set_thumbnail(url = member.avatar.url if member.avatar else str(member.default_avatar))
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(goodbye(bot))
