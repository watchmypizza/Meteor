import discord
from discord.ext import commands
from discord import app_commands
import dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

class DataTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countingconfig = "JSONS/config.json"
        self.levelconfig = "JSONS/levels.json"
        self.serverconfig = "JSONS/serverconfigs.json"
        self.forbiddenwords = "JSONS/forbidden_words.json"
        self.warnings_list = "JSONS/warnings.json"

    async def overwrite(self):
        def push_collection(filename: str, collection: str):
            with open(filename, "r") as f:
                data = json.load(f)

            for guild_id, config in data.items() if isinstance(data, dict) else [("global", data)]:
                if not isinstance(config, dict):
                    config = {"data": config}
                db.collection(collection).document(str(guild_id)).set(config)

        push_collection(self.countingconfig, "countingconfig")
        push_collection(self.levelconfig, "levels")
        push_collection(self.serverconfig, "serverconfigs")
        push_collection(self.forbiddenwords, "forbidden_words")
        push_collection(self.warnings_list, "warnings")

        return "success"

    @app_commands.command(name="transferdata", description="Developer only command.")
    async def transferdata(self, interaction: discord.Interaction):
        # Hardcoded dev check
        if interaction.user.id != 1116315001330880602:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return
        
        code = await self.overwrite()
        if code == "success":
            await interaction.response.send_message("Successfully transferred data.")
        else:
            await interaction.response.send_message("Failed to transfer data.")

async def setup(bot):
    await bot.add_cog(DataTransfer(bot))
