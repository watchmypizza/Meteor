import discord
from discord.ext import commands
from discord import app_commands
import humanfriendly
from datetime import timedelta
import os
import dotenv
from firebase_admin import credentials, firestore
import firebase_admin

env = dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_guild_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    @app_commands.command(name="mute", description="Mute a member for a time period.")
    @app_commands.describe(member="The member to mute.", time="The time to mute the member for.", reason="The reason for the mute")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, time: str, reason: str):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.")
            return
        try:
            await member.timeout(timedelta(seconds=humanfriendly.parse_timespan(time)), reason=reason)
            await interaction.response.send_message("Timed {} out for {} minutes.".format(member.mention, round(humanfriendly.parse_timespan(time)) / 60), ephemeral=True)
            csi = str(interaction.guild.id)
            if csi is None:
                return
            
            data = await self.get_guild_configs(csi)

            if data["mod_logs"] == 0:
                return

            ch = discord.utils.get(interaction.guild.channels, id=data["mod_logs"])
            embed = discord.Embed(
                title="Timeout",
                description=f"Member {member.mention} has been timed out for `{reason}` by {interaction.user.mention}"
            )
            await ch.send(embed=embed)        
        except discord.Forbidden:
            await interaction.response.send_message("I don't have the necessary permissions to mute this user.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(timeout(bot))