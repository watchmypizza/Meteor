import discord
from discord.ext import commands
from discord import app_commands
import humanfriendly
from datetime import timedelta
import os, json

class timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    def read(self, csi):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
            
        if csi not in data:
            data[csi] = {
                "mod_logs": 0
            }
        
        if "mod_logs" not in data[csi]:
            data[csi]["mod_logs"] = 0

        return data
    
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
            
            data = self.read(csi)

            if data[csi]["mod_logs"] == 0:
                return

            ch = discord.utils.get(interaction.guild.channels, id=data[csi]["mod_logs"])
            embed = discord.Embed(
                title="Timeout",
                description=f"Member {member.mention} has been timed out for `{reason}` by {interaction.user.mention}"
            )
            await ch.send(embed=embed)        
        except discord.Forbidden:
            await interaction.response.send_message("I don't have the necessary permissions to mute this user.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(timeout(bot))