import discord 
from discord.ext import commands
from discord import app_commands

class slashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="slash", description="Just for the badge")
    async def slash(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World!", ephemeral=True)
        return

async def setup(bot):
    await bot.add_cog(slashCog(bot))
    print("Slash cog loaded.")