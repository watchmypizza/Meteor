import discord
from discord.ext import commands
from discord import app_commands
import humanfriendly
from datetime import timedelta

class timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mute", description="Mute a member for a time period.")
    @app_commands.describe(member="The member to mute.", time="The time to mute the member for.", reason="The reason for the mute")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, time: str, reason: str):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.")
            return
        try:
            await member.timeout(timedelta(seconds=humanfriendly.parse_timespan(time)), reason=reason)
            await interaction.response.send_message("Timed {} out for {} minutes.".format(member.mention, round(humanfriendly.parse_timespan(time)) / 60), ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Couldn't mute user, I have no power.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(timeout(bot))