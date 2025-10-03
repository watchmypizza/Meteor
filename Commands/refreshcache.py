import discord
from discord.ext import commands, tasks
from firebase_admin import firestore, credentials
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

class RefreshCache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverconfigcache: dict[str, dict] = {}

    async def get_guild_configs(self, current_guild_id: str):
        if current_guild_id == "-5":
            configs = {}
            for doc in collection_ref.stream():
                configs[doc.id] = doc.to_dict()
            return configs

        snap = collection_ref.document(current_guild_id).get()
        return snap.to_dict() if snap.exists else {}

    @commands.command(name="refreshcache")
    async def manual_refresh(self, ctx: commands.Context):
        if ctx.author.id != 1116315001330880602:
            return
        self.serverconfigcache = await self.get_guild_configs("-5")
        await ctx.send(f"Cache manually refreshed at `{datetime.now().strftime('%H:%M:%S')}`")

async def setup(bot):
    await bot.add_cog(RefreshCache(bot))
