import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json = "JSONS/config.json"

    def read(self, current_server_id: str):
        if not os.path.exists(self.json) or os.path.getsize(self.json) == 0:
            data = {}
        else:
            with open(self.json, "r") as f:
                data = json.load(f)

        if current_server_id not in data:
            data[current_server_id] = {
                "counting_channel": 0,
                "started": False,
                "nofail": False,
                "current_count": 0,
                "delete_messages": True,
                "whitelisted_roles": [],
                "consecutive_counting": False
            }
            self.write(data)

        return data

    def write(self, data):
        with open(self.json, "w") as f:
            json.dump(data, f, indent=4)

    counting_group = app_commands.Group(name="counting", description="The counting settings and configurations")

    @counting_group.command(name="channel", description="Set the counting channel.")
    @app_commands.describe(channel="The channel to set as the counting channel.")
    async def counting_channel_subcommand(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return

        current_server_id = str(interaction.guild.id)
        data = self.read(current_server_id)
        data[current_server_id]["counting_channel"] = channel.id
        self.write(data)
        await interaction.response.send_message(f"The channel {channel.mention} has been selected as the counting channel.", ephemeral=True)

    @counting_group.command(name="start", description="Start the counting.")
    async def counting_start(self, interaction: discord.Interaction):
        current_server_id = str(interaction.guild.id)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return
        
        data = self.read(current_server_id)
        if data[current_server_id]["counting_channel"] == 0:
            await interaction.response.send_message("Please select a counting channel first with `/counting channel <channel>`.", ephemeral=True)
            return
        
        data[current_server_id]["started"] = True
        self.write(data)
        await interaction.response.send_message("Started counting.", ephemeral=True)
    
    @counting_group.command(name="stop", description="Stop the counting.")
    async def counting_stop(self, interaction: discord.Interaction):
        current_server_id = str(interaction.guild.id)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return
        
        data = self.read(current_server_id)
        if data[current_server_id]["counting_channel"] == 0:
            await interaction.response.send_message("Please select a counting channel first with `/counting channel <channel>`.", ephemeral=True)
            return
        
        data[current_server_id]["started"] = False
        self.write(data)
        await interaction.response.send_message("Stopped counting.", ephemeral=True)
    
    @counting_group.command(name="reset", description="Reset the count.")
    async def counting_reset(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have access to this command.", ephemeral=True)
            return

        current_server_id = str(interaction.guild.id)        
        data = self.read(current_server_id)
        data[current_server_id]["current_count"] = 0
        self.write(data)
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

        data = self.read(current_server_id)
        key = setting.value

        if key in ["started", "nofail", "delete_messages", "consecutive_counting"]:
            val = value.lower() in ("true", "yes", "1")
            data[current_server_id][key] = val

        elif key == "whitelisted_roles":
            role_ids = []
            for token in value.split():
                token = token.strip("<@&>")
                if token.isdigit():
                    role_ids.append(int(token))
            data[current_server_id]["whitelisted_roles"] = role_ids

        self.write(data)
        await interaction.response.send_message(
            f"The setting `{key}` has been updated to `{data[current_server_id][key]}`.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        else:
            current_server_id = str(message.guild.id)
            data = self.read(current_server_id)
        if message.channel.id != data[current_server_id]["counting_channel"]:
            return
        if not data[current_server_id]["started"]:
            return
        if message.author.bot:
            return

        user_role_ids = [role.id for role in message.author.roles]

        if message.content.isdigit():
            number = int(message.content)
            last_messages = [msg async for msg in message.channel.history(limit=1, before=message)]
            if last_messages:
                lastmsg = last_messages[0]
                if message.author.id == lastmsg.author.id and not data[current_server_id]["consecutive_counting"]:
                    await message.delete()
                    return
            if number == data[current_server_id]["current_count"] + 1:
                data[current_server_id]["current_count"] += 1
                self.write(data)
            else:
                if data[current_server_id]["nofail"]:
                    if any(role_id in data[current_server_id]["whitelisted_roles"] for role_id in user_role_ids):
                        return
                    await message.delete()
                else:
                    if any(role_id in data[current_server_id]["whitelisted_roles"] for role_id in user_role_ids):
                        return
                    data[current_server_id]["current_count"] = 0
                    self.write(data)
                    channel = message.channel
                    await channel.send(f"{message.author.mention} ruined the count! Reset to 0.")
        else:
            if data[current_server_id]["delete_messages"]:
                await message.delete()

async def setup(bot):
    await bot.add_cog(counting(bot))
