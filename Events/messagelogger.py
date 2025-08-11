import discord
from discord.ext import commands
from typing import Optional

def create_embed(user: discord.Member, action, before: discord.Message, after: Optional[discord.Message] = None):
    if action == "deleted":
        embed = discord.Embed(
            description=f"{user.mention} has deleted a message!\n\n`{before.content}`"
        )
    elif action == "edited":
        embed = discord.Embed(
            description=f"{user.mention} has edited a message!\n\n`{before.content}`\nto\n`{after.content}`"
        )
    return embed

class messagelogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        chat_logs = discord.utils.get(message.guild.channels, id=1403775143351943208)
        embed = create_embed(message.author, "deleted", message)
        await chat_logs.send(embed=embed)
        if message.attachments:
            files = [await attachment.to_file() for attachment in message.attachments]
            await chat_logs.send(files=files)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        chat_logs = discord.utils.get(before.guild.channels, id=1403775143351943208)
        embed = create_embed(before.author, "edited", before, after)
        await chat_logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(messagelogger(bot))
    print("Message Logger event cog loaded.")