import discord
from discord.ext import commands
from discord import app_commands
import os
import firebase_admin
from firebase_admin import credentials, firestore
import dotenv 

env = dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("countingconfig")

class counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        
        default = {
            "counting_channel": 0,
            "started": False,
            "nofail": False,
            "delete_messages": False,
            "whitelisted_roles": [],
            "current_count": 0,
            "consecutive_counting": False
        }

        await self.update_guild_config(guild_id, default)
        return default

    async def update_guild_config(self, guild_id: str, data: dict):
        doc_ref = collection_ref.document(guild_id)
        doc_ref.set(data, merge=True)

    counting_group = app_commands.Group(name="counting", description="The counting settings and configurations")

    @counting_group.command(name="channel", description="Set the counting channel.")
    @app_commands.describe(channel="The channel to set as the counting channel.")
    async def counting_channel_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return

        current_server_id = str(interaction.guild.id)
        data = await self.get_guild_config(current_server_id)
        data["counting_channel"] = channel.id
        await self.update_guild_config(current_server_id, data)
        await interaction.response.send_message(f"The channel {channel.mention} has been selected as the counting channel.", ephemeral=True)

    @counting_group.command(name="start", description="Start the counting.")
    async def counting_start(self, interaction: discord.Interaction):
        current_server_id = str(interaction.guild.id)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return
        
        data = await self.get_guild_config(current_server_id)
        if data["counting_channel"] == 0:
            await interaction.response.send_message("Please select a counting channel first with `/counting channel <channel>`.", ephemeral=True)
            return
        
        data["started"] = True
        await self.update_guild_config(current_server_id, data)
        await interaction.response.send_message("Started counting.", ephemeral=True)
    
    @counting_group.command(name="stop", description="Stop the counting.")
    async def counting_stop(self, interaction: discord.Interaction):
        current_server_id = str(interaction.guild.id)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return
        
        data = await self.get_guild_config(current_server_id)
        if data["counting_channel"] == 0:
            await interaction.response.send_message("Please select a counting channel first with `/counting channel <channel>`.", ephemeral=True)
            return
        
        data["started"] = False
        await self.update_guild_config(current_server_id, data)
        await interaction.response.send_message("Stopped counting.", ephemeral=True)
    
    @counting_group.command(name="reset", description="Reset the count.")
    async def counting_reset(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return

        current_server_id = str(interaction.guild.id)        
        data = await self.get_guild_config(current_server_id)
        data["current_count"] = 0
        await self.update_guild_config(current_server_id. data)
        await interaction.response.send_message("The count has been reset.", ephemeral=True)

    @counting_group.command(name="configure", description="Configure counting settings.")
    @app_commands.describe(
        setting="The setting you want to configure",
        value="The value to assign to that setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="started", value="started"),
            app_commands.Choice(name="nofail", value="nofail"),
            app_commands.Choice(name="delete_messages", value="delete_messages"),
            app_commands.Choice(name="whitelisted_roles", value="whitelisted_roles"),
            app_commands.Choice(name="consecutive_counting", value="consecutive_counting")
        ]
    )
    async def counting_configure(self, interaction: discord.Interaction, setting: app_commands.Choice[str], value: str):
        current_server_id = str(interaction.guild.id)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return

        data = await self.get_guild_config(current_server_id)
        key = setting.value

        if key in ["started", "nofail", "delete_messages", "consecutive_counting"]:
            val = value.lower() in ("true", "yes", "1")
            data[key] = val

        elif key == "whitelisted_roles":
            role_ids = []
            for token in value.split():
                token = token.strip("<@&>")
                if token.isdigit():
                    role_ids.append(int(token))
            data["whitelisted_roles"] = role_ids

        await self.update_guild_config(current_server_id, data)
        await interaction.response.send_message(
            f"The setting `{key}` has been updated to `{data[key]}`.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        else:
            current_server_id = str(message.guild.id)
            data = await self.get_guild_config(current_server_id)
        if message.channel.id != data["counting_channel"]:
            return
        if not data["started"]:
            return
        if message.author.bot:
            return

        user_role_ids = [role.id for role in message.author.roles]

        if message.content.isdigit():
            number = int(message.content)
            last_messages = [msg async for msg in message.channel.history(limit=1, before=message)]
            if last_messages:
                lastmsg = last_messages[0]
                if message.author.id == lastmsg.author.id and not data["consecutive_counting"]:
                    await message.delete()
                    return
            if number == data["current_count"] + 1:
                data["current_count"] += 1
                await self.update_guild_config(current_server_id, data)
            else:
                if data["nofail"]:
                    if any(role_id in data["whitelisted_roles"] for role_id in user_role_ids):
                        return
                    await message.delete()
                else:
                    if any(role_id in data["whitelisted_roles"] for role_id in user_role_ids):
                        return
                    data["current_count"] = 0
                    await self.update_guild_config(current_server_id, data)
                    channel = message.channel
                    await channel.send(f"{message.author.mention} ruined the count! Reset to 0.")
        else:
            if data["delete_messages"]:
                if any(role_id in data["whitelisted_roles"] for role_id in user_role_ids):
                    return
                await message.delete()

async def setup(bot):
    await bot.add_cog(counting(bot))
