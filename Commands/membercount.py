import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
import os
import dotenv
from firebase_admin import credentials, firestore
import firebase_admin

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class memcount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_guild_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    @app_commands.command(name="membercount", description="Fetch all members and display as a number.")
    async def membercount(self, interaction: discord.Interaction):
        csi = str(interaction.guild.id)
        data = await self.get_guild_configs(csi)
        if data["bot_role"] == 0: 
            mem_count = 0
            for member in interaction.guild.members:
                mem_count += 1
            embed = discord.Embed(
                title="Members",
                description=mem_count,
                color=discord.Color.random()
            )
            time_now = datetime.now().strftime("%H:%M")
            embed.set_footer(text="Today at " + str(time_now))
            await interaction.response.send_message(embed=embed)
        else:
            exclude_role = discord.utils.get(interaction.guild.roles, id=1403062164100612239)
            mem_count = 0
            for member in interaction.guild.members:
                if not exclude_role in member.roles:
                    mem_count += 1
            embed = discord.Embed(
                title="Members",
                description=mem_count,
                color=discord.Color.random()
            )
            time_now = datetime.now().strftime("%H:%M")
            embed.set_footer(text="Today at " + str(time_now))
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(memcount(bot))