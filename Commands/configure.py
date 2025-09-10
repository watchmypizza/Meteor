import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class configure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.json) or os.path.getsize(self.json) == 0:
            data = {}
        else:
            with open(self.json, "r") as f:
                data = json.load(f)
        
        if current_server_id not in data:
            data[current_server_id] = {
                "logging_channel": 0,
                "welcomer_channel": 0,
                "level_roles": [],
                "staff_roles": [],
                "ann_channel": 0,
                "bot_role": 0,
                "mod_logs": 0,
                "suggestion_channel": 0
            }
        
        return data
    
    def write(self, data):
        with open(self.json, "w") as f:
            json.dump(data, f, indent=4)

    configure_group = app_commands.Group(name="configure", description="Configure the bot!!")

    @configure_group.command(name="logging", description="Message logging channel.")
    @app_commands.describe(channel="The channel to set as the logging channel.")
    async def logging_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)
            return
        
        current_server_id = str(interaction.guild.id)
        data = self.read(current_server_id)
        data[current_server_id]["logging_channel"] = channel.id
        self.write(data)
        await interaction.response.send_message("Set the current logging channel to {}".format(channel.mention), ephemeral=True)

    @configure_group.command(name="welcomer", description="Welcomer and goodbye embeds!")
    @app_commands.describe(channel="The channel to send welcome and goodbye embeds.")
    async def welcomer_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)
            return

        csi = str(interaction.guild.id)
        data = self.read(csi)
        data[csi]["welcomer_channel"] = channel.id
        self.write(data)
        await interaction.response.send_message("Set the current welcomer channel to {}".format(channel.mention), ephemeral=True)

    @configure_group.command(name="levelroles", description="Set a number of level roles corresponding to each level. [10 roles supported only.]")
    @app_commands.describe(role="The role to set.", level="The level to set it to")
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove")
    ])
    async def levelroles_subcommand(self, interaction: discord.Interaction, role: discord.Role, level: int, action: app_commands.Choice[str]):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.", ephemeral=True
            )
            return
        
        csi = str(interaction.guild.id)
        data = self.read(csi)

        if action.value == "remove":
            for i, pair in enumerate(data[csi]["level_roles"]):
                if pair["level"] == level:
                    del data[csi]["level_roles"][i]
                    self.write(data)
                    await interaction.response.send_message(
                        f"Removed level {level} role.", ephemeral=True
                    )
                    return
        
        if "level_roles" not in data[csi]:
            data[csi]["level_roles"] = []
        
        for i, pair in enumerate(data[csi]["level_roles"]):
            if pair["level"] == level:
                data[csi]["level_roles"][i] = {"level": level, "role_id": role.id}
                self.write(data)
                await interaction.response.send_message(
                    f"Updated level {level} role to {role.mention}.", ephemeral=True
                )
                return
        
        data[csi]["level_roles"].append({"level": level, "role_id": role.id})
        self.write(data)
        await interaction.response.send_message(
            f"Added role {role.mention} for level {level}.", ephemeral=True
        )

    @configure_group.command(name="announcement", description="The channel to post announcements in.")
    @app_commands.describe(channel="The channel to send the announcements in")
    async def announcemenets_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.", ephemeral=True
            )
            return

        csi = str(interaction.guild.id)
        data = self.read(csi)
        data[csi]["ann_channel"] = channel.id
        self.write(data)
        await interaction.response.send_message(
            f"Set the announcements channel to {channel.mention}.", ephemeral=True
        )
    
    @configure_group.command(name="botrole", description="The bot role to ignore when executing membercount.")
    @app_commands.describe(role="The role to ignore when executing membercount.")
    async def botrole_subcommand(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.", ephemeral=True
            )
            return

        csi = str(interaction.guild.id)
        data = self.read(csi)
        data[csi]["bot_role"] = role.id
        self.write(data)
        await interaction.response.send_message("Set the bot role to {}".format(role.mention), ephemeral=True)

    @configure_group.command(name="modlogs", description="The channel to log mod actions inside of.")
    @app_commands.describe(channel="The channel to log mod actions inside of.")
    async def logs_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.", ephemeral=True
            )
            return
        
        csi = str(interaction.guild.id)
        data = self.read(csi)
        data[csi]["mod_logs"] = channel.id
        self.write(data)

        await interaction.response.send_message(f"Successfully set the logging channel to {channel.mention}", ephemeral=True)

    @configure_group.command(name="suggestions", description="Configure the suggestions channel")
    @app_commands.describe(channel="The suggestions channel")
    async def suggestions_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.", ephemeral=True
            )
            return

        csi = str(interaction.guild.id)
        data = self.read(csi)
        data[csi]["suggestion_channel"] = channel.id
        self.write(data)

        await interaction.response.send_message(f"Successfully set the suggestions channel to {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(configure(bot))