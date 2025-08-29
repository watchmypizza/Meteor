import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os
import json
from typing import Optional

class warncmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = "JSONS/warnings.json"

    def read(self, current_server_id):
        if not os.path.exists(self.warnings) or os.path.getsize(self.warnings) == 0:
            data = {}
        else:
            with open(self.warnings, "r") as f:
                data = json.load(f)

        if current_server_id not in data:
            data[current_server_id] = {
                "warnings": 0,
                "warning_list": []
            }

        return data

    def write(self, data):
        with open(self.warnings, "w") as f:
            json.dump(data, f, indent=4)

    @app_commands.command(name="warn", description="Warn a user for a reason.")
    @app_commands.describe(user="The user you are warning", reason="The reason for the warning")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
            return
        
        csi = str(interaction.guild.id)

        data = self.read(csi)
        user_id = str(user.id)

        if user_id not in data[csi]:
            data[csi][user_id] = {"warnings": 0, "warning_list": []}

        data[csi][user_id]["warnings"] += 1

        new_warning = {
            "reason": reason,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data[csi][user_id]["warning_list"].append(new_warning)

        self.write(data)

        await interaction.response.send_message(f"{user.mention} has been warned for: `{reason}`. They now have {data[csi][str(user.id)]['warnings']} warnings.", ephemeral=True)

    @app_commands.command(name="warnings", description="View warnings for a user.")
    @app_commands.describe(user="The user to view warnings for (defaults to yourself)")
    async def warnings(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        csi = str(interaction.guild.id)

        target_user = user if user is not None else interaction.user

        is_ephemeral = target_user == interaction.user 

        if target_user != interaction.user:
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message("You do not have permission to view warnings for other users.", ephemeral=True)
                return

        data = self.read(csi)
        user_id = str(target_user.id)

        if user_id not in data[csi] or not data[csi][user_id]["warning_list"]:
            await interaction.response.send_message(f"{target_user.display_name} has no warnings.", ephemeral=True)
            return

        warnings_list = data[csi][user_id]["warning_list"]
        total_warnings = data[csi][user_id]["warnings"]

        embed = discord.Embed(
            title=f"Warnings for {target_user.display_name}",
            color=discord.Color.orange()
        )

        reversed_warnings_list = warnings_list[::-1]

        for index, warning in enumerate(reversed_warnings_list, start=1):
            warning_number = total_warnings - index + 1
            embed.add_field(
                name=f"Warning {warning_number}",
                value=f"Reason: `{warning['reason']}`\nTimestamp: {warning['timestamp']}",
                inline=False
            )

        embed.set_footer(text=f"Total warnings: {total_warnings}")

        await interaction.response.send_message(embed=embed, ephemeral=is_ephemeral)

    @app_commands.command(name="removewarn", description="Remove a specific warning for a user.")
    @app_commands.describe(user="The user to remove a warning from", warning_number="The number of the warning to remove")
    async def removewarn(self, interaction: discord.Interaction, user: discord.Member, warning_number: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
            return

        csi = str(interaction.guild.id)

        data = self.read(csi)
        user_id = str(user.id)

        if user_id not in data[csi] or not data[csi][user_id]["warning_list"]:
            await interaction.response.send_message(f"{user.display_name} has no warnings to remove.", ephemeral=True)
            return

        warnings_list = data[csi][user_id]["warning_list"]
        total_warnings = len(warnings_list)

        if not 1 <= warning_number <= total_warnings:
            await interaction.response.send_message(f"Invalid warning number. This user has {total_warnings} warnings (1-{total_warnings}).", ephemeral=True)
            return

        index_to_remove = warning_number - 1

        try:
            removed_warning_reason = warnings_list[index_to_remove]["reason"]
            removed_warning = data[csi][user_id]["warning_list"].pop(index_to_remove)
            data[csi][user_id]["warnings"] -= 1
            self.write(data)
            await interaction.response.send_message(f"Successfully removed Warning {warning_number} for {user.display_name} (Reason: `{removed_warning_reason}`). They now have {data[csi][user_id]['warnings']} warnings.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(warncmd(bot))