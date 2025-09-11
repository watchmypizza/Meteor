import discord
from discord.ext import commands
from typing import Optional
import os
import dotenv
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

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
    
    async def get_guild_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild == None:
            return
        try:
            current_server_id = str(message.guild.id)
        except AttributeError:
            return
        data = await self.get_guild_configs(current_server_id)
        if data["logging_channel"] == 0:
            return
        chat_logs = discord.utils.get(message.guild.channels, id=data["logging_channel"])
        embed = create_embed(message.author, "deleted", message)
        await chat_logs.send(embed=embed)
        if message.attachments:
            files = [await attachment.to_file() for attachment in message.attachments]
            await chat_logs.send(files=files)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:
            current_server_id = str(after.guild.id)
        except AttributeError:
            return
        data = await self.get_guild_configs(current_server_id)
        if data["logging_channel"] == 0:
            return
        chat_logs = discord.utils.get(before.guild.channels, id=data["logging_channel"])
        embed = create_embed(before.author, "edited", before, after)
        await chat_logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(messagelogger(bot))