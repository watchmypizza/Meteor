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
        self.config = "JSONS/serverconfigs.json"
        self.time_now = datetime.now().strftime("%H:%M")
    
    def read(self, server_id):
        if not os.path.exists(self.levels) or os.path.getsize(self.levels) == 0:
            data = {}
        else:
            with open(self.levels, "r") as f:
                data = json.load(f)
        if server_id not in data:
            data[server_id] = {}
        return data
    
    def write(self, data):
        with open(self.levels, "w") as f:
            json.dump(data, f, indent=4)
    
    def read_config(self, server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        if server_id not in data:
            data[server_id] = {"level_roles": []}
        if "level_roles" not in data[server_id]:
            data[server_id]["level_roles"] = []
        if "excluded_level_channels" not in data[server_id]:
            data[server_id]["excluded_level_channels"] = []
        return data
    
    def write_config(self, data, server_id):
        with open(self.config, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        
        server_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        # Load data
        levels_data = self.read(server_id)
        config_data = self.read_config(server_id)

        if message.channel.id in config_data[server_id]["excluded_level_channels"]:
            return

        # Ensure user exists
        if user_id not in levels_data[server_id]:
            levels_data[server_id][user_id] = {"xp": 0, "level": 0, "xp_needed": 50, "level_lock": False, "total_xp": 0}

        if "level_lock" not in levels_data[server_id][user_id]:
            levels_data[server_id][user_id]["level_lock"] = False
        
        if "total_xp" not in levels_data[server_id][user_id]:
            levels_data[server_id][user_id]["total_xp"] = 0
        
        if levels_data[server_id][user_id]["level_lock"] == True:
            return

        # Add XP
        leveled_up = False
        levels_data[server_id][user_id]["xp"] += 5
        levels_data[server_id][user_id]["total_xp"] += 5
        if levels_data[server_id][user_id]["xp"] >= levels_data[server_id][user_id]["xp_needed"]:
            levels_data[server_id][user_id]["level"] += 1
            levels_data[server_id][user_id]["xp"] = 0
            levels_data[server_id][user_id]["xp_needed"] += 50 + (levels_data[server_id][user_id]["level"] ** 2 * 100)
            leveled_up = True
        
        self.write(levels_data)

        if leveled_up:
            user_level = levels_data[server_id][user_id]["level"]
            guild = message.guild

            level_roles = sorted(config_data[server_id]["level_roles"], key=lambda x: x["level"])

            for pair in level_roles:
                level_required = pair["level"]
                role_id = pair["role_id"]

                if user_level >= level_required:
                    role = discord.utils.get(guild.roles, id=role_id)
                    if role:
                        if role in message.author.roles:
                            continue
                        try:
                            if user_level == level_required and role not in message.author.roles:
                                await message.author.add_roles(role)
                        except discord.Forbidden:
                            print(f"Missing permissions to give role {role.name}")
                        except discord.HTTPException as e:
                            print(f"HTTPException: {e}")
                    else:
                        print(f"Role with ID {role_id} not found in guild {guild.name}.")
                else:
                    print("Could not get guild from message.")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        csi = str(message.guild.id)
        if csi == None:
            return
        if message.author.id == self.bot.user.id:
            return

        data = self.read(csi)
        config_data = self.read_config(csi)

        if message.channel.id in config_data[csi]["excluded_level_channels"]:
            return
        
        if data[csi][str(message.author.id)]["level_lock"] == True:
            return

        if str(message.author.id) not in data[csi]:
            data[csi][str(message.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        if data[csi][str(message.author.id)]["xp"] <= 0:
            data[csi][str(message.author.id)]["xp"] = 0
        else:
            data[csi][str(message.author.id)]["xp"] -= 5
            data[csi][str(message.author.id)]["total_xp"] -= 5
        self.write(data)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:
            csi = str(before.guild.id)
        except AttributeError:
            return
        if csi == None:
            return
        if before.author.id == self.bot.user.id:
            return
        
        data = self.read(csi)
        config_data = self.read_config(csi)
        if before.channel.id in config_data[csi]["excluded_level_channels"]:
            return

        if data[csi][str(before.author.id)]["level_lock"] == True:
            return

        if str(before.author.id) not in data[csi]:
            data[csi][str(before.author.id)] = {"xp": 0, "level": 0, "xp_needed": 50}
        
        if len(str(before.content)) > len(str(after.content)):
            if data[csi][str(before.author.id)]["xp"] <= 0:
                data[csi][str(before.author.id)]["xp"] = 0
            else:
                data[csi][str(before.author.id)]["xp"] -= 5
                data[csi][str(before.author.id)]["total_xp"] -= 5
            self.write(data)

    levelgroup = app_commands.Group(name="level", description="Check your level and xp")
    @levelgroup.command(name="show", description="Check your level and xp")
    @app_commands.describe(user="The user to check the level of.")
    async def level(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        csi = str(interaction.guild.id)
        if csi == None:
            return
        if user:
            data = self.read(csi)
            if str(user.id) not in data[csi]:
                await interaction.response.send_message("This user does not have any stats to show!")
                return
            
            xp = data[csi][str(user.id)]["xp"]
            level = data[csi][str(user.id)]["level"]
            xp_needed = data[csi][str(user.id)]["xp_needed"]

            embed = discord.Embed(
                title=user.name,
                description=f"Level: {level}\nXP: {xp}\nXP until next level: {xp_needed}",
                color=discord.Color.random()
            )
            
            embed.set_footer(text="Today at " + self.time_now)
            await interaction.response.send_message(embed=embed)
            return
        
        data = self.read(csi)

        user_id = str(interaction.user.id)
        if user_id not in data[csi]:
            data[csi][user_id] = {"xp": 0, "level": 0, "xp_needed": 50}

        user_data = data[csi][user_id]
        xp = user_data["xp"]
        level = user_data["level"]
        xp_needed = user_data["xp_needed"]

        embed = discord.Embed(
            title=interaction.user.name,
            description=f"Level: {level}\nXP: {xp}\nXP until next level: {xp_needed}",
            color=discord.Color.random()
        )
        embed.set_footer(text="Today at " + self.time_now)
        await interaction.response.send_message(embed=embed)
    
    @levelgroup.command(name="lock", description="Lock a user's level.")
    @app_commands.describe(user="The user to level lock")
    async def levellock(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.")
            return
        
        csi = str(interaction.guild.id)
        if csi == None:
            return
        
        data = self.read(csi)
        if str(user.id) not in data[csi]:
            data[csi][str(user.id)] = {"xp": 0, "level": 0, "xp_needed": 50, "level_lock": False}
        
        if data[csi][str(user.id)]["level_lock"] == True:
            data[csi][str(user.id)]["level_lock"] = False
            await interaction.response.send_message("Level has been unlocked for user {}.".format(user.mention), ephemeral=True)
        else:
            data[csi][str(user.id)]["level_lock"] = True
            await interaction.response.send_message("Level has been locked for user {}.".format(user.mention), ephemeral=True)
        
        self.write(data)
    
    @levelgroup.command(name="set", description="Set a user's level.")
    @app_commands.describe(user="User to moderate", operation="The operation to execute", value="The level to set the user to.")
    @app_commands.choices(operation=[
        app_commands.Choice(name="level", value="level"),
        app_commands.Choice(name="xp", value="xp")
    ])
    async def levelset(self, interaction: discord.Interaction, user: discord.Member, operation: str, value: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.")
            return
        
        csi = str(interaction.guild.id)
        if csi == None:
            return

        data = self.read(csi)
        if str(user.id) not in data[csi]:
            data[csi][str(user.id)] = {"xp": 0, "level": 0, "xp_needed": 50, "level_lock": False}

        if operation == "level":
            calculated_xp_needed = 50 + (value ** 2 * 100)
            data[csi][str(user.id)]["level"] = value
            data[csi][str(user.id)]["xp_needed"] = calculated_xp_needed
            await interaction.response.send_message("Level has been set to {} for user {}.".format(value, user.mention), ephemeral=True)
        elif operation == "xp":
            if value >= data[csi][str(user.id)]["xp_needed"]:
                data[csi][str(user.id)]["level"] += 1
                data[csi][str(user.id)]["xp_needed"] += 150
            data[csi][str(user.id)]["xp"] = value
            await interaction.response.send_message("XP has been set to {} for user {}.".format(value, user.mention), ephemeral=True)
        
        self.write(data)
    
    @levelgroup.command(name="exclude", description="Exclude a channel from earning xp/levels in.")
    @app_commands.describe(channel="The channel to exclude")
    async def levelexclude(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to use this command.")
            return
        
        csi = str(interaction.guild.id)
        if csi == None:
            return

        data = self.read_config(csi)
        
        excluded_level_channels = data[csi]["excluded_level_channels"]
        if channel.id not in excluded_level_channels:
            excluded_level_channels.append(channel.id)
        else:
            excluded_level_channels.remove(channel.id)
            self.write_config(data, csi)
            await interaction.response.send_message("Channel {} has been included in earning xp/levels in.".format(channel.mention), ephemeral=True)
            return
        
        self.write_config(data, csi)
        await interaction.response.send_message("Channel {} has been excluded from earning xp/levels in.".format(channel.mention), ephemeral=True)
    
    @levelgroup.command(name="leaderboard", description="Check the leaderboard of the server.")
    async def levelleaderboard(self, interaction: discord.Interaction):
        csi = str(interaction.guild.id)
        if csi == None:
            return
        
        data = self.read(csi)

        leaderboard = []
        users = data[csi]
        sorted_users = sorted(users.items(), key=lambda x: x[1]["total_xp"], reverse=True)
        embed = discord.Embed(
            title="Leaderboard",
            description="Top 10 users with the most XP",
            color=discord.Color.random()
        )
        for i, (user_id, user_data) in enumerate(sorted_users[:10]):
            user = interaction.guild.get_member(int(user_id))
            if user is None:
                continue
            xp = user_data["xp"]
            level = user_data["level"]
            xp_needed = user_data["xp_needed"]
            leaderboard.append(f"{i+1}. {user.name} - Level: {level} - XP: {xp} - XP until next level: {xp_needed}")
            embed.add_field(name=f"{i+1}. {user.name}", value=f"Level: {level} - XP: {xp} - XP until next level: {xp_needed}", inline=False)
        
        embed.set_footer(text="Today at " + self.time_now)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(levelsystem(bot))