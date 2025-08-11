import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands

class memcount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="membercount", description="Fetch all members and display as a number.")
    async def membercount(self, interaction: discord.Interaction):
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
    print("MEMCOUNT cog loaded.")