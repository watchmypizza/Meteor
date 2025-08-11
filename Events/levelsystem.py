import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import datetime
from typing import Optional

class levelsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = "levels.json"
        self.time_now = datetime.now().strftime("%H:%M")
    
    def read(self):
        with open(self.levels, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
            return data

    def write(self, data):
        with open(self.levels, "w") as f:
            json.dump(data, f)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        data = self.read()
        if str(message.author.id) not in data:
            data[str(message.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        if data[str(message.author.id)]["xp"] >= data[str(message.author.id)]["xp_needed"]:
            data[str(message.author.id)]["xp_needed"] += 150
            data[str(message.author.id)]["level"] += 1
        data[str(message.author.id)]["xp"] += 5
        self.write(data)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        data = self.read()
        if str(message.author.id) not in data:
            data[str(message.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        data[str(message.author.id)]["xp"] -= 5
        self.write(data)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.id == self.bot.user.id:
            return
        
        data = self.read()
        if str(before.author.id) not in data:
            data[str(before.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        
        if len(str(before.content)) > len(str(after.content)):
            data[str(before.author.id)]["xp"] -= 5
            self.write(data)

    @app_commands.command(name="level", description="Check your level and xp")
    @app_commands.describe(user="The user to check the level of.")
    async def level(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        if user:
            data = self.read()
            if str(user.id) not in data:
                await interaction.response.send_message("This user does not have any stats to show!")
                return
            
            xp = data[str(user.id)]["xp"]
            level = data[str(user.id)]["level"]
            xp_needed = data[str(user.id)]["xp_needed"]

            embed = discord.Embed(
                title=user.name,
                description=f"Level: {level}\nXP: {xp}\nXP until next level: {xp_needed}",
                color=discord.Color.random()
            )
            
            embed.set_footer(text="Today at " + self.time_now)
            await interaction.response.send_message(embed=embed)
            return
        
        with open(self.levels, "r") as f:
            data = json.load(f)
            if str(interaction.user.id) not in data:
                data[str(interaction.user.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
            xp = data[str(interaction.user.id)]["xp"]
            level = data[str(interaction.user.id)]["level"]
            xp_needed = data[str(interaction.user.id)]["xp_needed"]

            embed = discord.Embed(
                title=interaction.user.name,
                description=f"Level: {level}\nXP: {xp}\nXP until next level: {xp_needed}",
                color=discord.Color.random()
            )
            
            embed.set_footer(text="Today at " + self.time_now)
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(levelsystem(bot))
    print("LEVELSYSTEM cog loaded.")