import discord
from discord.ext import commands
import os
import dotenv
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_config(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        csi = str(member.guild.id)
        if csi is None:
            return
        data = await self.get_guild_config(csi)
        if data["welcomer_channel"] == 0:
            return
        embed = discord.Embed(
            title=f"Welcome, {member.name}",
            description=f"Welcome to {member.guild.name}! {member.mention}",
            color=discord.Color.random()
        )
        url = member.avatar.url if member.avatar else str(member.default_avatar)
        embed.set_thumbnail(url=url)
        embed.set_footer(text=f"ID: {member.id}")
        
        welcome_ch = discord.utils.get(member.guild.channels, id=data["welcomer_channel"])
        await welcome_ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(welcomer(bot))