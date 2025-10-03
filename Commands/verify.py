import discord
from discord.ext import commands
from discord import app_commands
import firebase_admin
import random
import dotenv
import os
from firebase_admin import credentials, firestore

env = dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
serverconfigs = db.collection("serverconfigs")

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(verify.VerifyView(bot))
    
    async def read(self, guild_id):
        doc_ref = serverconfigs.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        
        default = {}
        return default
    
    def generate_code(self):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789', k=6))

    class VerifyView(discord.ui.View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            button = discord.ui.Button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
            issue = discord.ui.Button(label="Can't verify?", style=discord.ButtonStyle.red, custom_id="issue_button")

            button.callback = self.verify_button_callback
            issue.callback = self.issue_button_callback

            self.add_item(button)
            self.add_item(issue)

        async def verify_button_callback(self, interaction: discord.Interaction):
            generated_code = self.bot.get_cog("verify").generate_code()
            modal = self.bot.get_cog("verify").VerifyModal(self.bot, generated_code)
            await interaction.response.send_modal(modal)

        async def issue_button_callback(self, interaction: discord.Interaction):
            await interaction.response.send_message("If you are having issues verifying, please go to the support channel and open a ticket.", ephemeral=True)

    class VerifyModal(discord.ui.Modal, title="Verification"):
        def __init__(self, bot, generated_code):
            super().__init__(timeout=None)
            self.bot = bot
            self.generated_code = generated_code
            
            self.code = discord.ui.TextInput(
                label=f"Enter this code to verify: {self.generated_code}",
                placeholder="Code",
                max_length=6
            )
            self.add_item(self.code)
        
        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value == self.generated_code:
                await interaction.response.defer(ephemeral=True)
                data = await self.bot.get_cog("verify").read(str(interaction.guild.id))
                guild_id = str(interaction.guild.id)
                role_id = int(data["verified_role"])
                role = interaction.guild.get_role(role_id)
                if role is None:
                    return await interaction.response.send_message("The role set for this server no longer exists. Please contact an administrator.", ephemeral=True)
                await interaction.user.add_roles(role)
            else:
                await interaction.response.send_message("Incorrect code. Please try again.", ephemeral=True)
            return


    @app_commands.command(name="verify", description="Post the verification message.")
    async def verifycmd(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
        
        data = await self.read(str(interaction.guild.id))
        if data == -1:
            return await interaction.response.send_message("An error occurred while reading the configuration file. Please contact the bot developer.", ephemeral=True)

        embed = discord.Embed(title="Verification", description="Click below button to start the verification process.", color=0x00ff00)
        view = verify.VerifyView(self.bot)
        await interaction.response.send_message("Verification message sent.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(verify(bot))