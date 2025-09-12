import discord
from discord.ext import commands, tasks
from typing import Optional
import os
import dotenv
import asyncio
from firebase_admin import credentials, firestore
from datetime import datetime

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
        self.serverconfigcache = {}
        self.config_refresh_cache.start()
    
    async def get_guild_configs(self, current_guild_id: str):
        if current_guild_id == "-5":
            configs = {}
            docs = collection_ref.stream()
            for doc in docs:
                configs[doc.id] = doc.to_dict()
            return configs
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    @tasks.loop(minutes=3)
    async def config_refresh_cache(self):
        self.serverconfigcache = await self.get_guild_configs("-5")
        print(f"[MessageLogger] Serversettings cache updated at {datetime.now()}")
    
    @config_refresh_cache.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild == None:
            return
        try:
            current_server_id = str(message.guild.id)
        except AttributeError:
            return
        data = self.serverconfigcache.get(current_server_id, {})
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
        data = self.serverconfigcache.get(current_server_id, {})
        if data["logging_channel"] == 0:
            return
        chat_logs = discord.utils.get(before.guild.channels, id=data["logging_channel"])
        embed = create_embed(before.author, "edited", before, after)
        await chat_logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(messagelogger(bot))