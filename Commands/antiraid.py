import discord
from discord import app_commands
from discord.ext import commands, tasks
from firebase_admin import credentials, firestore
import firebase_admin
import os
import dotenv

dotenv.load_dotenv(".env")
service = os.getenv("FIREBASE_JSON")
creds = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(creds)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class antiraid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    raid_group = app_commands.Group(name="antiraid", description="Anti Raid measures")

    async def _check_admin(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have the necessary permissions to execute this command!", ephemeral=True)
            return False
        return True

    @raid_group.command(name="lock", description="Locks the channel the command is executed in")
    async def raid_lock(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        try:
            cur_channel = interaction.channel
            overwrites = cur_channel.overwrites_for(interaction.guild.default_role)
            overwrites.send_messages = False
            await cur_channel.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason="Lockdown initiated by {}".format(interaction.user))
            await interaction.response.send_message("{} has been locked down.".format(cur_channel.mention), ephemeral=True)
        except KeyError as e:
            await interaction.response.send_message("Make sure you have a verified role and a staff role set up!", ephemeral=True)
    
    @raid_group.command(name="unlock", description="Unlock the current channel you are in")
    async def raid_unlock(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        try:
            cur_channel = interaction.channel
            overwrites = cur_channel.overwrites_for(interaction.guild.default_role)
            overwrites.send_messages = True
            await cur_channel.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason="Lockdown initiated by {}".format(interaction.user))
            await interaction.response.send_message("{} has been unlocked.".format(cur_channel.mention), ephemeral=True)
        except KeyError as e:
            await interaction.response.send_message("Make sure you have a verified role and a staff role set up!", ephemeral=True)

    @raid_group.command(name="serverlock", description="Lockdown all of the server except staff-only categories")
    async def raid_server_lock(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        raw_categories = config.get("staff_categories")
        staff_category_ids = set(raw_categories if isinstance(raw_categories, list) else ([raw_categories] if raw_categories else []))

        if not staff_category_ids:
            await interaction.response.send_message("Make sure you set up a staff category!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        default_role = interaction.guild.default_role
        reason = f"Server lockdown initiated by {interaction.user}"

        for channel in interaction.guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                if channel.id in staff_category_ids:
                    continue
            else:
                if getattr(channel, "category_id", None) in staff_category_ids:
                    continue

            overwrites = channel.overwrites_for(default_role)
            overwrites.send_messages = False
            await channel.set_permissions(default_role, overwrite=overwrites, reason=reason)

        await interaction.followup.send("Locked every channel down.", ephemeral=True)
    
    @raid_group.command(name="serverunlock", description="Lift lockdown all of the server except staff-only categories")
    async def raid_server_unlock(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        raw_categories = config.get("staff_categories")
        staff_category_ids = set(raw_categories if isinstance(raw_categories, list) else ([raw_categories] if raw_categories else []))

        if not staff_category_ids:
            await interaction.response.send_message("Make sure you set up a staff category!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        default_role = interaction.guild.default_role
        reason = f"Server lockdown lifted by {interaction.user}"

        for channel in interaction.guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                if channel.id in staff_category_ids:
                    continue
            else:
                if getattr(channel, "category_id", None) in staff_category_ids:
                    continue

            overwrites = channel.overwrites_for(default_role)
            overwrites.send_messages = True
            await channel.set_permissions(default_role, overwrite=overwrites, reason=reason)

        await interaction.followup.send("Lifted the lockdown on every channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(antiraid(bot))
