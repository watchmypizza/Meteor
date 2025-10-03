from discord.ext import commands, tasks
from firebase_admin import credentials, firestore
import discord
import firebase_admin
import os, dotenv
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
       self.serverconfigcache: dict[str, dict] = {}
       self.refresh_cache.start()
  
   async def get_guild_configs(self, current_guild_id: str):
       if current_guild_id == "-5":
           configs = {}
           for doc in collection_ref.stream():
               configs[doc.id] = doc.to_dict()
           return configs

       snap = collection_ref.document(current_guild_id).get()
       return snap.to_dict() if snap.exists else {}

   @tasks.loop(minutes=1)
   async def refresh_cache(self):
       self.serverconfigcache = await self.get_guild_configs("-5")
       print(f"[Prefix] Serversettings cache updated at {datetime.now()}")

   @refresh_cache.before_loop
   async def before_refresh(self):
       await self.bot.wait_until_ready()

   def cog_unload(self):
       self.refresh_cache.cancel()

   @commands.Cog.listener()
   async def on_message(self, message: discord.Message):
       if message.author.bot:
           return
          
async def setup(bot):
   await bot.add_cog(getPrefix(bot))
