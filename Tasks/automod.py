import discord
from discord.ext import commands
import humanfriendly
from datetime import datetime
from datetime import timedelta
import dotenv
import os
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("forbidden_words")

class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def read_forbidden_words(self):
        doc_ref = collection_ref.document("forbidden_words")
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        forbidden_words_list = await self.read_forbidden_words()
        if forbidden_words_list is None:
            return
        for word in forbidden_words_list:
            if word in message.content.lower():
                timeout_duration = humanfriendly.parse_timespan("1 hour")
                timeout_until = datetime.now().astimezone() + timedelta(seconds=timeout_duration)
                try:
                    await message.delete()
                    await message.author.timeout(timeout_until, reason="Golden Rule")
                except discord.Forbidden:
                    await message.channel.send("I don't have permission to time out this user.")
                except Exception as e:
                    print(e)

async def setup(bot):
    await bot.add_cog(automod(bot))