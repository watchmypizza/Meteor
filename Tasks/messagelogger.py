import discord
from discord.ext import commands
from typing import Optional
import os
import json

def create_embed(user: discord.Member, action, before: discord.Message, after: Optional[discord.Message] = None):
    if action == "deleted":
        embed = discord.Embed(
            description=f"{user.mention} has deleted a message!\n\n`{before.content}`"
        )
    elif action == "edited":
        embed = discord.Embed(
            description=f"{user.mention} has edited a message!\n\n`{before.content}` -> `{after.content}`"
        )
    return embed

class messagelogger(commands.Cog):
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
                "logging_channel": 0
            }
        
        return data

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild == None:
            return
        current_server_id = str(message.guild.id)
        data = self.read(current_server_id)
        if data[current_server_id]["logging_channel"] == 0:
            return
        chat_logs = discord.utils.get(message.guild.channels, id=data[current_server_id]["logging_channel"])
        embed = create_embed(message.author, "deleted", message)
        await chat_logs.send(embed=embed)
        if message.attachments:
            files = [await attachment.to_file() for attachment in message.attachments]
            await chat_logs.send(files=files)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        current_server_id = str(after.guild.id)
        data = self.read(current_server_id)
        if data[current_server_id]["logging_channel"] == 0:
            return
        chat_logs = discord.utils.get(before.guild.channels, id=data[current_server_id]["logging_channel"])
        embed = create_embed(before.author, "edited", before, after)
        await chat_logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(messagelogger(bot))