import discord
from discord.ext import commands
from discord import app_commands
import os
import firebase_admin
from firebase_admin import credentials, firestore
import dotenv

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")


class configure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        default = {
            "logging_channel": 0,
            "welcomer_channel": 0,
            "level_roles": [],
            "staff_roles": [],
            "ann_channel": 0,
            "bot_role": 0,
            "mod_logs": 0,
            "suggestion_channel": 0,
            "excluded_level_channels": [],
            "prefix": ''
        }
        await self.update_guild_config(guild_id, default)
        return default

    async def update_guild_config(self, guild_id: str, data: dict):
        doc_ref = collection_ref.document(guild_id)
        doc_ref.set(data, merge=True)

    configure_group = app_commands.Group(name="configure", description="Configure the bot!")

    async def _check_admin(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.",
                ephemeral=True
            )
            return False
        return True

    @configure_group.command(name="logging", description="Message logging channel.")
    @app_commands.describe(channel="The channel to set as the logging channel.")
    async def logging_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["logging_channel"] = channel.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message(f"Set the logging channel to {channel.mention}", ephemeral=True)

    @configure_group.command(name="welcomer", description="Welcomer and goodbye embeds!")
    @app_commands.describe(channel="The channel to send welcome and goodbye embeds.")
    async def welcomer_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["welcomer_channel"] = channel.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message(f"Set the welcomer channel to {channel.mention}", ephemeral=True)

    @configure_group.command(name="levelroles", description="Set a number of level roles corresponding to each level.")
    @app_commands.describe(role="The role to set.", level="The level to set it to")
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove")
    ])
    async def levelroles_subcommand(self, interaction: discord.Interaction, role: discord.Role, level: int, action: app_commands.Choice[str]):
        if not await self._check_admin(interaction):
            return
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)

        if "level_roles" not in config:
            config["level_roles"] = []

        if action.value == "remove":
            config["level_roles"] = [pair for pair in config["level_roles"] if pair["level"] != level]
            await self.update_guild_config(guild_id, config)
            await interaction.response.send_message(f"Removed level {level} role.", ephemeral=True)
            return

        updated = False
        for pair in config["level_roles"]:
            if pair["level"] == level:
                pair["role_id"] = role.id
                updated = True
                break
        if not updated:
            config["level_roles"].append({"level": level, "role_id": role.id})

        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message(f"Set role {role.mention} for level {level}.", ephemeral=True)

    @configure_group.command(name="announcement", description="The channel to post announcements in.")
    @app_commands.describe(channel="The channel to send the announcements in")
    async def announcement_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["ann_channel"] = channel.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message(f"Set the announcements channel to {channel.mention}", ephemeral=True)

    
    @configure_group.command(name="botrole", description="The bot role to ignore when executing membercount.")
    @app_commands.describe(role="The role to ignore when executing membercount.")
    async def botrole_subcommand(self, interaction: discord.Interaction, role: discord.Role):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["bot_role"] = role.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message(f"Set the bot role to {role.mention}", ephemeral=True)
 
    @configure_group.command(name="modlogs", description="The channel to log mod actions inside of.")
    @app_commands.describe(channel="The channel to log mod actions inside of.")
    async def logs_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["mod_logs"] = channel.id
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message(f"Successfully set the logging channel to {channel.mention}", ephemeral=True)

    @configure_group.command(name="suggestions", description="Configure the suggestions channel")
    @app_commands.describe(channel="The suggestions channel")
    async def suggestions_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["suggestion_channel"] = channel.id
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message(f"Successfully set the suggestions channel to {channel.mention}", ephemeral=True)

    @configure_group.command(name="prefix", description="Set a custom server prefix")
    @app_commands.describe(prefix="The prefix to set it to.")
    async def prefix_subcommand(self, interaction: discord.Interaction, prefix: str):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["prefix"] = prefix
        await self.update_guild_config(guild_id, data)

        await interaction.response.send_message("Successfully updated the prefix to {}.".format(prefix), ephemeral=True)

async def setup(bot):
    await bot.add_cog(configure(bot))