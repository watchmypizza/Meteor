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
            "prefix": '',
            "ai_automod_enabled": "False"
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
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message("Successfully updated the prefix to {}.".format(prefix), ephemeral=True)
    
    @commands.command(name="newprefix")
    async def newprefix(self, ctx, prefix: str):
        if not ctx.author.guild_permissions.administrator:
            return
        
        guild_id = str(ctx.guild.id)
        config = await self.get_guild_config(guild_id)
        config["prefix"] = prefix
        await self.update_guild_config(guild_id, config)

        await ctx.send("Successfully updated the prefix to {}.".format(prefix))
    
    @configure_group.command(name="resetprefix", description="Reset the current prefix back to default")
    async def resetprefix_subcommand(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["prefix"] = "$ "
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message("Successfully reset the prefix to {}.".format(config["prefix"]), ephemeral=True)
    
    @configure_group.command(name="verifiedrole", description="Sets a role to give the user once verified.")
    @app_commands.describe(role="The role to give the user.")
    async def verifiedrole_subcommand(self, interaction: discord.Interaction, role: discord.Role):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["verified_role"] = role.id
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message("Successfully updated the verified role to {}.".format(role.mention), ephemeral=True)

    @configure_group.command(name="level_channel", description="Set the channel to announce level ups in.")
    @app_commands.describe(channel="The channel to announce level ups in")
    async def level_up_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["level_channel"] = channel.id
        await self.update_guild_config(guild_id, config)

        await interaction.response.send_message("Successfully set the channel to {}".format(channel.mention), ephemeral=True)

    @configure_group.command(name="staff", description="This is needed for the tickets to work.")
    @app_commands.describe(staff_role="The staff role for the tickets")
    async def staff_subcommand(self, interaction: discord.Interaction, staff_role: discord.Role):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["staff_roles"] = staff_role.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message("Successfully set the staff role to {}!".format(staff_role.mention), ephemeral=True)

    @configure_group.command(name="ticketlogs", description="The channel to log ticket creation / deletion in.")
    @app_commands.describe(channel="The channel to log the tickets in")
    async def ticketlogs_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["ticketlogs"] = channel.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message("Successfully set the ticket logs channel to {}!".format(channel.mention), ephemeral=True)

    @configure_group.command(name="aiautomod", description="Enable or disable the AI automod")
    @app_commands.describe(state="On or Off state")
    @app_commands.choices(state=[
        app_commands.Choice(name="On", value="True"),
        app_commands.Choice(name="Off", value="False")
    ])
    async def aiautomod_subcommand(self, interaction: discord.Interaction, state: app_commands.Choice[str]):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        if state.value == "True":
            config["ai_automod_enabled"] = "True"
            await self.update_guild_config(guild_id, config)
            await interaction.response.send_message("Successfully enabled the AI automod.", ephemeral=True)
        else:
            config["ai_automod_enabled"] = "False"
            await self.update_guild_config(guild_id, config)
            await interaction.response.send_message("Successfully disabled the AI automood.", ephemeral=True)

    @configure_group.command(name="staffcategory", description="Add a staff category to the anti raid command.")
    @app_commands.describe(operation="Add or remove from the list", category="The category to add/remove")
    @app_commands.choices(operation=[
        app_commands.Choice(name="Add", value="append"),
        app_commands.Choice(name="Remove", value="remove")
    ])
    async def staffcat_subcommand(self, interaction: discord.Interaction, operation: app_commands.Choice[str], category: discord.CategoryChannel):
        if not await self._check_admin(interaction):
            return
        
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        categories = list(config.get("staff_categories", []))
        if operation.value == "append":
            if category.id not in categories:
                categories.append(category.id)
                await interaction.response.send_message("Successfully added `{}` to the list.".format(category.name), ephemeral=True)
            else:
                await interaction.response.send_message("That category is already in the list.", ephemeral=True)
                return
        elif operation.value == "remove":
            try:
                categories.remove(category.id)
                await interaction.response.send_message("Successfully removed `{}` from the list.".format(category.name), ephemeral=True)
            except ValueError:
                await interaction.response.send_message("That category isn't in the list.", ephemeral=True)
                return

        config["staff_categories"] = categories
        await self.update_guild_config(guild_id, config)

async def setup(bot):
    await bot.add_cog(configure(bot))