import discord
from discord.ext import commands
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials, firestore
import dotenv

env = dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class postwall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        default = {}

    @commands.command()
    async def wall(self, ctx, *, arg: str=None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have sudo privileges to execute this command.")
            return

        if arg is None:
            await ctx.send("Invalid arguments. Use `wall <message>`")
        
        csi = str(ctx.guild.id)
        data = await self.get_guild_config(csi)

        if data["ann_channel"] == 0:
            return

        ch = discord.utils.get(ctx.guild.text_channels, id=data["ann_channel"])
        cur_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        await ch.send(f"""```
        Broadcast message from root@{ctx.author.name} ({cur_time}):
        
        {arg}```""")

async def setup(bot):
    await bot.add_cog(postwall(bot))