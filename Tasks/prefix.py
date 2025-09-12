import discord
from discord.ext import commands, tasks
import os, dotenv
from firebase_admin import credentials, firestore
import firebase_admin
from datetime import datetime

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class getPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverconfigcache = {}
        self.refresh_cache.start()
    
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
    async def refresh_cache(self):
        self.serverconfigcache = await self.get_guild_configs("-5")
        print(f"[Prefix] Serversettings cache updated at {datetime.now()}")

    @refresh_cache.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if str(message.guild.id) == None:
                return
        except AttributeError:
            return
        
        data = self.serverconfigcache.get(str(message.guild.id), {})
        content = message.content
        if data["prefix"] in content[0]:
            print("test")
            # I still have to implement command execution functionality here

async def setup(bot):
    await bot.add_cog(getPrefix(bot))