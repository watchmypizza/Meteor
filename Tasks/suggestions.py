import discord
from discord.ext import commands
import os, asyncio
import dotenv
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    async def get_server_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        current_server_id = str(message.guild.id)
        if current_server_id is None:
            return

        data = await self.get_server_configs(current_server_id)

        try:
            if data["suggestion_channel"] != 0 and message.channel.id == data["suggestion_channel"]:
                await message.add_reaction("✅")
                await asyncio.sleep(.1)
                await message.add_reaction("❌")
            else:
                return
        except KeyError:
            return

async def setup(bot):
    await bot.add_cog(suggestions(bot))