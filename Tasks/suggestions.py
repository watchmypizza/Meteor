import discord
from discord.ext import commands
import os, json, asyncio

class suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        
        if not current_server_id in data:
            data = {}
        
        if not "suggestion_channel" in data[current_server_id]:
            data[current_server_id]["suggestion_channel"] = 0
        
        return data
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        current_server_id = str(message.guild.id)
        if current_server_id is None:
            return

        data = self.read(current_server_id)

        try:
            if data[current_server_id]["suggestion_channel"] != 0 and message.channel.id == data[current_server_id]["suggestion_channel"]:
                await message.add_reaction("✅")
                await asyncio.sleep(.1)
                await message.add_reaction("❌")
            else:
                return
        except KeyError:
            return

async def setup(bot):
    await bot.add_cog(suggestions(bot))