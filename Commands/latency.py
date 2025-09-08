import discord
from discord.ext import commands
from discord import app_commands

class botlatency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="latency", description="Measure your latency to the bot!")
    async def latency(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=True)

async def setup(bot):
    await bot.add_cog(botlatency(bot))