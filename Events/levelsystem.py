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
        self.levels = "JSONS/levels.json"
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

        levellist = [
            "5", "10", "15", "20", "25", "30", "35", "40", "45", "50",
            "55", "60", "65", "70", "75", "80", "85", "90", "95", "100"
        ]

        levelroles = [
            1410315739138887700, # lv 5
            1410316223085936830, # lv 10
            1410316330892136539, # lv 15
            1410316527663579216, # lv 20
            1410316604063088882, # lv 25
            1410316686166458430, # lv 30
            1410316940827689062, # lv 35
            1410317033018626069, # lv 40
            1410317120625184800, # lv 45
            1410317257896366090, # lv 50
            1410317339362201672, # lv 55
            1410317504433094666, # lv 60
            1410317574297751562, # lv 65
            1410317629469626368, # lv 70
            1410317689653825640, # lv 75
            1410317748860620800, # lv 80
            1410317829676470424, # lv 85
            1410317983892508753, # lv 90
            1410318046731702403, # lv 95
            1410318217854849165, # lv 100
        ]

        data = self.read()
        if str(message.author.id) not in data:
            data[str(message.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}

        leveled_up = False
        if data[str(message.author.id)]["xp"] >= data[str(message.author.id)]["xp_needed"]:
            data[str(message.author.id)]["xp_needed"] += 150
            data[str(message.author.id)]["level"] += 1
            data[str(message.author.id)]["xp"] = 0
            leveled_up = True

        data[str(message.author.id)]["xp"] += 5
        self.write(data)

        if leveled_up:
            current_level = str(data[str(message.author.id)]["level"])
            if current_level in levellist:
                level_index = levellist.index(current_level)
                role_id = levelroles[level_index]
                guild = message.guild

                if guild:
                    role = discord.utils.get(guild.roles, id=role_id)
                    if role:
                        if role not in message.author.roles:
                            try:
                                await message.author.add_roles(role)
                                print(f"Gave {message.author.name} the {role.name} role.")
                            except discord.Forbidden:
                                print(f"Missing permissions to add role {role.name} to {message.author.name}.")
                            except discord.HTTPException as e:
                                print(f"Failed to add role {role.name} to {message.author.name}: {e}")
                    else:
                        print(f"Role with ID {role_id} not found in guild {guild.name}.")
                else:
                    print("Could not get guild from message.")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        data = self.read()
        if str(message.author.id) not in data:
            data[str(message.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        if data[str(message.author.id)]["xp"] == 0:
            return
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
            if data[str(message.author.id)]["xp"] == 0:
                return
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