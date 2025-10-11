import os
import re
import random
from typing import Optional, List, Dict

import dotenv
import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View, Modal
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")
service = os.getenv("FIREBASE_JSON")
creds = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(creds)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

STYLE_MAP: Dict[str, ButtonStyle] = {
    "primary": ButtonStyle.primary,
    "secondary": ButtonStyle.secondary,
    "success": ButtonStyle.success,
    "danger": ButtonStyle.danger,
    "link": ButtonStyle.link,
}

def _normalize_style(style_str: Optional[str]) -> str:
    if not style_str:
        return "secondary"
    s = style_str.strip().lower()
    return s if s in STYLE_MAP else "secondary"

class ticketsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ticketsystem.ticketViewOrigServer(bot))
        self.bot.add_view(ticketsystem.ticketView(bot))

    async def _check_admin(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You do not have the necessary permissions to use this command.",
                ephemeral=True
            )
            return False
        return True

    async def get_guild_config(self, guild_id: str) -> dict:
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        default = {
            "staff_roles": 0,
            "ticket_category": 0,
            "ticketlogs": 0,
            "buttons": []
        }
        return default

    async def update_guild_config(self, guild_id: str, data: dict):
        doc_ref = collection_ref.document(guild_id)
        doc_ref.set(data, merge=True)

    ticketsystem_group = app_commands.Group(name="ticket", description="The ticket system")

    def generate_ticket_handle(self) -> str:
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))

    class ticketViewOrigServer(View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            btn_report = Button(label="Report Member", style=ButtonStyle.danger, custom_id="report_member")
            btn_verify = Button(label="Verification issues", style=ButtonStyle.primary, custom_id="verify_issue")
            btn_bug    = Button(label="Report a bug", style=ButtonStyle.success, custom_id="bug")

            btn_report.callback = self.report_member_callback
            btn_verify.callback = self.issue_callback
            btn_bug.callback    = self.bug_callback

            self.add_item(btn_report)
            self.add_item(btn_bug)
            self.add_item(btn_verify)

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

            btn_report = Button(label="Report Member", style=ButtonStyle.danger, custom_id="report_member")
            btn_verify = Button(label="Verification issues", style=ButtonStyle.primary, custom_id="verify_issue")

            btn_report.callback = self.report_member_callback
            btn_verify.callback = self.issue_callback

            self.add_item(btn_report)
            self.add_item(btn_verify)

        async def report_member_callback(self, interaction: discord.Interaction):
            generated_handle = self.bot.get_cog("ticketsystem").generate_ticket_handle()
            modal = self.bot.get_cog("ticketsystem").userReportModal(self.bot, generated_handle)
            await interaction.response.send_modal(modal)

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

            if "archived" in name:
                await interaction.response.send_message(
                    "Please execute this command inside of an active ticket.", ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)
            config = await self.bot.get_cog("ticketsystem").get_guild_config(guild_id)

            ticketlogs = discord.utils.get(interaction.guild.channels, id=config.get("ticketlogs", 0))
            if ticketlogs is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: ticket logs channel is not set.", ephemeral=True
                )
                return

            staff_role = discord.utils.get(interaction.guild.roles, id=config.get("staff_roles", 0))
            if staff_role is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: staff role is not set.", ephemeral=True
                )
                return

            cur_date = datetime.now()
            converted_date = cur_date.strftime("%d・%m・%Y // %H:%M")

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)
            }

            if "ticket" in name:
                new_name = re.sub(r"^ticket", "ticket-archived", name)
            else:
                new_name = re.sub(r"^bug", "bug-archived", name)

            await interaction.channel.edit(name=new_name, overwrites=overwrites)
            embed = discord.Embed(
                title="Ticket closed",
                description=f"Ticket closed by {interaction.user.mention} at {converted_date}",
                color=discord.Color.red()
            )
            await ticketlogs.send(embed=embed)
            await interaction.response.send_message("Ticket archived.", ephemeral=True)

    class userReportModal(Modal, title="Report a member"):
        def __init__(self, bot, generated_handle: str):
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
            cog = self.bot.get_cog("ticketsystem")
            config = await cog.get_guild_config(guild_id)

            staff_role = discord.utils.get(interaction.guild.roles, id=config.get("staff_roles", 0))
            if staff_role is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: staff role not set.", ephemeral=True
                )
                return

            category = None
            if config.get("ticket_category", 0):
                category = discord.utils.get(interaction.guild.categories, id=config["ticket_category"])

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, manage_channels=True)
            }

            name_prefix = "ticket-"
            if category:
                channel = await interaction.guild.create_text_channel(name=name_prefix + self.generated_handle, category=category, overwrites=overwrites)
            else:
                channel = await interaction.guild.create_text_channel(name=name_prefix + self.generated_handle, overwrites=overwrites)

            ticketlogs = discord.utils.get(interaction.guild.channels, id=config.get("ticketlogs", 0))
            if ticketlogs is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: ticket logs channel not set.", ephemeral=True
                )
                return

            embed = discord.Embed(
                title="Member Report",
                description=f"{interaction.user.mention} has opened a ticket!",
                color=discord.Color.green()
            )

            reported_member = None
            try:
                reported_member = await interaction.guild.fetch_member(int(self.member_to_report.value))
            except Exception:
                pass

            embed.add_field(name="Member reported", value=reported_member.mention if reported_member else f"(invalid id: {self.member_to_report.value})", inline=True)
            embed.add_field(name="Brief overview", value=str(self.issue_overview.value), inline=True)
            embed.add_field(name="GoTo Ticket", value=channel.mention, inline=True)

            await interaction.response.send_message(f"Ticket has been created at {channel.mention}!", ephemeral=True)

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
        def __init__(self, bot, generated_handle: str):
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
            cog = self.bot.get_cog("ticketsystem")
            config = await cog.get_guild_config(guild_id)

            staff_role = discord.utils.get(interaction.guild.roles, id=config.get("staff_roles", 0))
            if staff_role is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: staff role not set.", ephemeral=True
                )
                return

            category = None
            if config.get("ticket_category", 0):
                category = discord.utils.get(interaction.guild.categories, id=config["ticket_category"])

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, manage_channels=True)
            }

            name_prefix = "bug-"
            if category:
                channel = await interaction.guild.create_text_channel(name=name_prefix + self.generated_handle, category=category, overwrites=overwrites)
            else:
                channel = await interaction.guild.create_text_channel(name=name_prefix + self.generated_handle, overwrites=overwrites)

            ticketlogs = discord.utils.get(interaction.guild.channels, id=config.get("ticketlogs", 0))
            if ticketlogs is None:
                await interaction.response.send_message(
                    "Ticket system misconfigured: ticket logs channel not set.", ephemeral=True
                )
                return

            embed = discord.Embed(
                title="Bug Report",
                description=f"{interaction.user.mention} has opened a ticket!",
                color=discord.Color.green()
            )
            embed.add_field(name="Brief overview", value=str(self.issue_overview.value), inline=True)
            embed.add_field(name="GoTo Ticket", value=channel.mention, inline=True)

            await interaction.response.send_message(f"Ticket has been created at {channel.mention}!", ephemeral=True)
            ticket_embed = discord.Embed(
                title=str(self.issue_overview.value),
                description=str(self.issue_description),
                color=discord.Color.blurple()
            )
            await channel.send("Staff will be with you shortly! Please wait up to 15 minutes before pinging anyone of the team.")
            await channel.send(embed=ticket_embed)
            await ticketlogs.send(embed=embed)

    def make_button_view_from_config(self, config: dict) -> View:
        v = View(timeout=None)
        for b in config.get("buttons", []):
            label = str(b.get("label", "Button"))
            style = STYLE_MAP.get(_normalize_style(b.get("style")), ButtonStyle.secondary)
            custom_id = f"ticketbtn:{label}"

            btn = Button(label=label, style=style, custom_id=custom_id)

            async def _cb(interaction: discord.Interaction, label=label):
                generated = self.generate_ticket_handle()
                if label.lower().startswith("report"):
                    await interaction.response.send_modal(self.userReportModal(self.bot, generated))
                else:
                    await interaction.response.send_modal(self.issueReportModal(self.bot, generated))

            btn.callback = _cb
            v.add_item(btn)
        return v

    @ticketsystem_group.command(name="setup", description="Set the ticket system up (posts a message in the current channel).")
    async def ticketsystem_setup(self, interaction: discord.Interaction):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)

        if config.get("staff_roles", 0) == 0:
            await interaction.response.send_message("Please configure the ticket system with `/configure staff`.", ephemeral=True)
            return

        if config.get("ticketlogs", 0) == 0:
            await interaction.response.send_message("Please configure the ticket system with `/configure ticketlogs`.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Problem? Create a ticket!",
            description="You can create a ticket for multiple things, such as a member violating the rules or you having a question! Our staff are there to help you.",
            color=discord.Color.dark_purple()
        )

        if config.get("buttons"):
            view = self.make_button_view_from_config(config)
        else:
            if interaction.user.id == 1116315001330880602:
                view = ticketsystem.ticketViewOrigServer(self.bot)
            else:
                view = ticketsystem.ticketView(self.bot)

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Setup message sent.", ephemeral=True)

    @ticketsystem_group.command(name="category", description="The category to create new tickets in.")
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
            return

        embed = discord.Embed(
            title="Close ticket?",
            color=discord.Color.red()
        )
        view = ticketsystem.closeTicketView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ticketsystem_group.command(name="button", description="Add, modify or remove a button.")
    @app_commands.describe(
        action="Add, modify, or remove a button",
        button="The current label of the button to modify/remove",
        new_text="New text for the added/modified button",
        color="Button color: primary, secondary, success, danger, link"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="modify", value="modify")
    ])
    async def ticketsystem_button(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        button: Optional[str] = None,
        new_text: Optional[str] = None,
        color: Optional[str] = None
    ):
        if not await self._check_admin(interaction):
            return

        guild_id = str(interaction.guild.id)
        config = await self.get_guild_config(guild_id)
        buttons: List[Dict[str, str]] = list(config.get("buttons", []))

        def fmt_buttons(lst):
            if not lst:
                return "_(no buttons configured)_"
            return "\n".join(f"- **{b['label']}** · `{b['style']}`" for b in lst)

        match action.value:
            case "add":
                if not new_text:
                    await interaction.response.send_message("Please provide `new_text` for the new button.", ephemeral=True)
                    return
                style_str = _normalize_style(color)
                buttons.append({"label": new_text, "style": style_str})
                msg = f"Added button **{new_text}** with style `{style_str}`."

            case "remove":
                if not button:
                    await interaction.response.send_message("Please provide `button` (existing label) to remove.", ephemeral=True)
                    return
                before = len(buttons)
                buttons = [b for b in buttons if b["label"] != button]
                if len(buttons) == before:
                    await interaction.response.send_message(f"Button **{button}** not found.", ephemeral=True)
                    return
                msg = f"Removed button **{button}**."

            case "modify":
                if not button or not new_text:
                    await interaction.response.send_message("Please provide both `button` (existing label) and `new_text`.", ephemeral=True)
                    return
                style_str = _normalize_style(color) if color else None
                for b in buttons:
                    if b["label"] == button:
                        old_label = b["label"]
                        b["label"] = new_text
                        if style_str:
                            b["style"] = style_str
                        msg = f"Modified **{old_label}** to **{b['label']}** (style `{b['style']}`)."
                        break
                else:
                    await interaction.response.send_message(f"Button **{button}** not found.", ephemeral=True)
                    return

        config["buttons"] = buttons
        await self.update_guild_config(guild_id, config)

        embed = discord.Embed(
            title="Ticket buttons updated",
            description=f"{msg}\n\n**Current buttons:**\n{fmt_buttons(buttons)}",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ticketsystem(bot))
