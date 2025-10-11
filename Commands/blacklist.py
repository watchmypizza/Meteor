import json
import discord
from discord.ext import commands, tasks
from discord import app_commands
from firebase_admin import firestore, credentials
import firebase_admin
from datetime import datetime, timezone
import os
import dotenv
from typing import Iterable

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
blacklist_ref = db.collection("blacklist")
serverconfigs_ref = db.collection("serverconfigs")

class blacklisting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blacklistcache: dict[str, dict] = {}
        self.refresh_cache.start()

    def _get_all_blacklisted(self) -> dict[str, dict]:
        return {doc.id: doc.to_dict() for doc in blacklist_ref.stream()}

    def _get_blacklist_doc(self, guild_id: str) -> dict:
        snap = blacklist_ref.document(guild_id).get()
        return snap.to_dict() if snap.exists else {}

    def _delete_serverconfigs_many(self, guild_ids: Iterable[str]) -> None:
        for gid in guild_ids:
            serverconfigs_ref.document(str(gid)).delete()

    def _write_blacklist(self, guild_id: str, note: str) -> dict:
        payload = {"guild_id": guild_id, "note": note, "created_at": firestore.SERVER_TIMESTAMP}
        blacklist_ref.document(guild_id).set(payload, merge=False)
        return payload

    async def get_blacklist(self, guild_id: str):
        if guild_id == "-5":
            return await self.bot.loop.run_in_executor(None, self._get_all_blacklisted)
        return await self.bot.loop.run_in_executor(None, self._get_blacklist_doc, guild_id)

    async def destroy_guild_config(self, guild_id_or_ids):
        if isinstance(guild_id_or_ids, str):
            ids = [guild_id_or_ids]
        elif isinstance(guild_id_or_ids, dict):
            ids = list(guild_id_or_ids.keys())
        else:
            ids = list(guild_id_or_ids)
        await self.bot.loop.run_in_executor(None, self._delete_serverconfigs_many, ids)

    async def write_blacklist(self, guild_id: str, note: str):
        return await self.bot.loop.run_in_executor(None, self._write_blacklist, guild_id, note)

    @tasks.loop(minutes=1)
    async def refresh_cache(self):
        self.blacklistcache = await self.get_blacklist("-5")
        print(f"[Blacklist] Cache updated at {datetime.now(timezone.utc).isoformat()}")
        if self.blacklistcache:
            await self.destroy_guild_config(self.blacklistcache)
    @refresh_cache.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.refresh_cache.cancel()

    @app_commands.command(name="blacklist", description="Blacklist a server.")
    @app_commands.describe(server="Server ID to blacklist", note="Note for the blacklist")
    async def blacklist(self, interaction: discord.Interaction, server: str, note: str):
        if interaction.user.id != 1116315001330880602:
            return

        payload = await self.write_blacklist(server, note)
        await self.destroy_guild_config(server)
        self.blacklistcache[server] = payload
        await interaction.response.send_message(f"Server `{server}` has been blacklisted.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(blacklisting(bot))
