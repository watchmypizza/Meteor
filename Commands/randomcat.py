from discord.ext import commands
from discord import app_commands
import json
import discord
import requests

class randomcat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://api.thecatapi.com/v1/images/search"

    @app_commands.command(name="suki", description="RANDOM CAT IMAGE!!11!!111")
    async def suki(self, interaction: discord.Interaction):
        response = requests.get(self.url)
        data = response.json()
        image_url = data[0]['url']
        embed = discord.Embed(
            title="Meow"
        )
        embed.set_image(url=image_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(randomcat(bot))