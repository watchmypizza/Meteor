import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
import os, json

class memcount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        
        if current_server_id not in data:
            data = {
                "bot_role": 0
            }
        
        if "bot_role" not in data[current_server_id]:
            data[current_server_id]["bot_role"] = 0
        
        return data

    @app_commands.command(name="membercount", description="Fetch all members and display as a number.")
    async def membercount(self, interaction: discord.Interaction):
        csi = str(interaction.guild.id)
        data = self.read(csi)
        if data[csi]["bot_role"] == 0: 
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