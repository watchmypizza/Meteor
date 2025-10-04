import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from discord.ui import Button, View, Modal
from discord import ButtonStyle
from firebase_admin import credentials, firestore
import firebase_admin
import random
import dotenv
import re
import os
from datetime import datetime

dotenv.load_dotenv(".env")
service = os.getenv("FIREBASE_JSON")

creds = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(creds)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class ticketsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ticketsystem.ticketView(bot))

    async def _check_admin(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.",
                ephemeral=True
            )
            return False
        return True

    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        default = {
            "staff_roles": [],
            "ticket_category": 0
        }
        return default

    async def update_guild_config(self, guild_id: str, data: dict):
        doc_ref = collection_ref.document(guild_id)
        doc_ref.set(data, merge=True)

    ticketsystem_group = app_commands.Group(name="ticket", description="The ticket system")

    def generate_ticket_handle(self):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))

    class ticketViewOrigServer(View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            button = Button(label="Report Member", style=ButtonStyle.red, custom_id="report_member")
            issue = Button(label="Verification issues", style=ButtonStyle.blurple, custom_id="verify_issue")
            bug = Button(label="Report a bug", style=discord.ButtonStyle.green, custom_id="bug")

            button.callback = self.report_member_callback
            issue.callback = self.issue_callback
            bug.callback = self.bug_callback

            self.add_item(button)
            self.add_item(bug)
            self.add_item(issue)
        
        async def report_member_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").userReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)
        
        async def issue_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").issueReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)
        
        async def bug_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").issueReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)

    class ticketView(View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            button = Button(label="Report Member", style=ButtonStyle.red, custom_id="report_member")
            issue = Button(label="Verification issues", style=ButtonStyle.blurple, custom_id="verify_issue")

            button.callback = self.report_member_callback
            issue.callback = self.issue_callback

            self.add_item(button)
            self.add_item(issue)
        
        async def report_member_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").userReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)#
        
        async def issue_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").issueReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)
    
    class closeTicketView(View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            button = Button(label="Close ticket", style=ButtonStyle.danger, custom_id="close")

            button.callback = self.close_callback

            self.add_item(button)
        
        async def close_callback(self, interaction: discord.Interaction):
            name = interaction.channel.name
            if not ("ticket" in name or "bug" in name):
                await interaction.response.send_message(
                    "Please execute this command inside of a ticket.", ephemeral=True
                )
                return
            
            if "archived" in interaction.channel.name:
                await interaction.response.send_message("Please execute this command inside of a ticket.", ephemeral=True)
                return

            guild_id = str(interaction.guild.id)
            config = await self.bot.get_cog("ticketsystem").get_guild_config(guild_id)
            ticketlogs = discord.utils.get(interaction.guild.channels, id=config["ticketlogs"])
            cur_date = datetime.now()
            converted_date = cur_date.strftime("%d・%m・%Y // %H:%M")
            staff_role = discord.utils.get(interaction.guild.roles, id=config["staff_roles"])
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)
            }
            if "ticket" in name:
                match = re.sub(r"^ticket", "ticket-archived-", name)
                await interaction.channel.edit(name=match, overwrites=overwrites)
                embed = discord.Embed(
                    title="Ticket closed",
                    description="Ticket closed by {} at {}".format(interaction.user.mention, converted_date),
                    color=discord.Color.red()
                )
                await ticketlogs.send(embed=embed)
            if "bug" in name:
                match = re.sub(r"^bug", "bug-archived-", name)
                await interaction.channel.edit(name=match, overwrites=overwrites)
                embed = discord.Embed(
                    title="Ticket closed",
                    description="Ticket closed by {} at {}".format(interaction.user.mention, converted_date),
                    color=discord.Color.red()
                )
                await ticketlogs.send(embed=embed)
        
    class userReportModal(Modal, title="Report a member"):
        def __init__(self, bot, generated_handle):
            super().__init__(timeout=None)
            self.bot = bot
            self.generated_handle = generated_handle

            self.issue_overview = discord.ui.TextInput(
                label="Enter your issue in a short overview",
                placeholder="Toxicity",
                max_length=100,
                style=discord.TextStyle.short
            )
            self.issue_description = discord.ui.TextInput(
                label="Describe the issue in detail here",
                placeholder="Member is being very toxic and insulting everyone...",
                max_length=2000,
                style=discord.TextStyle.paragraph
            )
            self.member_to_report = discord.ui.TextInput(
                label="The Member to report (USER ID!!!)",
                placeholder="1116315001330880602",
                max_length=30,
                style=discord.TextStyle.short
            )
            self.add_item(self.issue_overview)
            self.add_item(self.issue_description)
            self.add_item(self.member_to_report)

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            config = await self.bot.get_cog("ticketsystem").get_guild_config(guild_id)
            staff_role = discord.utils.get(interaction.guild.roles, id=config["staff_roles"])
            if config["ticket_category"]:
                category = discord.utils.get(interaction.guild.categories, id=config["ticket_category"])
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, manage_channels=True) 
            }

            if config["ticket_category"]:
                channel = await interaction.guild.create_text_channel(name="bug-" + self.generated_handle, category=category, overwrites=overwrites)
            else:
                channel = await interaction.guild.create_text_channel(name="bug-" + self.generated_handle, overwrites=overwrites)

            ticketlogs = discord.utils.get(interaction.guild.channels, id=config["ticketlogs"])
            embed = discord.Embed(
                title="Member Report",
                description="{} has opened a ticket!".format(interaction.user.mention),
                color=discord.Color.green()
            )
            reported_member = await interaction.guild.fetch_member(self.member_to_report.value)
            embed.add_field(name="Member reported", value=reported_member.mention, inline=True)
            embed.add_field(name="Brief overview", value=str(self.issue_overview.value), inline=True)
            embed.add_field(name="GoTo Ticket", value=channel.mention, inline=True)
            await interaction.response.send_message("Ticket has been created at {}!".format(channel.mention), ephemeral=True)
            ticket_embed = discord.Embed(
                title=str(self.issue_overview.value),
                description=str(self.issue_description),
                color=discord.Color.blurple()
            )
            await channel.send("Staff will be with you shortly! Please wait up to 15 minutes before pinging anyone of the team.")
            await channel.send(embed=ticket_embed)
            await ticketlogs.send(staff_role.mention)
            await ticketlogs.send(embed=embed)
    
    class issueReportModal(Modal, title="Report a bug"):
        def __init__(self, bot, generated_handle):
            super().__init__(timeout=None)
            self.bot = bot
            self.generated_handle = generated_handle

            self.issue_overview = discord.ui.TextInput(
                label="Enter your issue in a short overview",
                placeholder="Bot doesnt work in my server",
                max_length=100,
                style=discord.TextStyle.short
            )
            self.issue_description = discord.ui.TextInput(
                label="Describe the issue in detail here",
                placeholder="The bot only responds: This interaction failed",
                max_length=2000,
                style=discord.TextStyle.paragraph
            )
            self.add_item(self.issue_overview)
            self.add_item(self.issue_description)
        
        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            config = await self.bot.get_cog("ticketsystem").get_guild_config(guild_id)
            staff_role = discord.utils.get(interaction.guild.roles, id=config["staff_roles"])
            if config["ticket_category"]:
                category = discord.utils.get(interaction.guild.categories, id=config["ticket_category"])
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, manage_channels=True) 
            }

            if config["ticket_category"]:
                channel = await interaction.guild.create_text_channel(name="bug-" + self.generated_handle, category=category, overwrites=overwrites)
            else:
                channel = await interaction.guild.create_text_channel(name="bug-" + self.generated_handle, overwrites=overwrites)

            ticketlogs = discord.utils.get(interaction.guild.channels, id=config["ticketlogs"])
            embed = discord.Embed(
                title="Bug Report",
                description="{} has opened a ticket!".format(interaction.user.mention),
                color=discord.Color.green()
            )
            embed.add_field(name="Brief overview", value=str(self.issue_overview.value), inline=True)
            embed.add_field(name="GoTo Ticket", value=channel.mention, inline=True)
            await interaction.response.send_message("Ticket has been created at {}!".format(channel.mention), ephemeral=True)
            ticket_embed = discord.Embed(
                title=str(self.issue_overview.value),
                description=str(self.issue_description),
                color=discord.Color.blurple()
            )
            await channel.send("Staff will be with you shortly! Please wait up to 15 minutes before pinging anyone of the team.")
            await channel.send(embed=ticket_embed)
            await ticketlogs.send(embed=embed)

    @ticketsystem_group.command(name="setup", description="Set the ticket system up (This will post a message in the channel you are currently in.)")
    async def ticketsystem_setup(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return
        
        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)

        if config["staff_roles"] == 0:
            await interaction.response.send_message("Please configure the ticket system with /configure staff")
            return
        
        if config["ticketlogs"] == 0:
            await interaction.response.send_message("Please configure the ticket system with /configure ticketlogs")
            return

        embed = discord.Embed(
            title="Problem? Create a ticket!",
            description="You can create a ticket for multiple things, such as a member violating the rules or you having a question! Our staff are there to help you.",
            color=discord.Color.dark_purple()
        )

        if interaction.user.id == 1116315001330880602:
            view = ticketsystem.ticketViewOrigServer(self.bot)
        else:
            view = ticketsystem.ticketView(self.bot)

        await interaction.channel.send(embed=embed, view=view)
    
    @ticketsystem_group.command(name="category", description="The category to create new tickets in")
    @app_commands.describe(category="The category to create tickets in.")
    async def ticketsystem_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        config["ticket_category"] = category.id
        await self.update_guild_config(guild_id, config)
        await interaction.response.send_message("Successfully set the ticket category!", ephemeral=True)
    
    @ticketsystem_group.command(name="close", description="Close a ticket")
    async def ticketsystem_close(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.",
                ephemeral=True
            )
            return False
        
        embed = discord.Embed(
            title="Close ticket?",
            color=discord.Color.red()
        )
        view = ticketsystem.closeTicketView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ticketsystem(bot))