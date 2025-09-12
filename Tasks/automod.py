import discord
from discord.ext import commands, tasks
import humanfriendly
from datetime import datetime, timedelta
import dotenv
import os
from firebase_admin import credentials, firestore
import firebase_admin

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("forbidden_words")


class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forbidden_words_cache = {}
        self.refresh_cache.start()

    async def read_forbidden_words(self):
        doc_ref = collection_ref.document("forbidden_words")
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    @tasks.loop(minutes=10)
    async def refresh_cache(self):
        self.forbidden_words_cache = await self.read_forbidden_words()
        print(f"[Automod] Forbidden words cache updated at {datetime.now()}")

    @refresh_cache.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        for word in self.forbidden_words_cache:
            if word.lower() in message.content.lower():
                timeout_duration = humanfriendly.parse_timespan("1 hour")
                timeout_until = datetime.now().astimezone() + timedelta(seconds=timeout_duration)
                try:
                    await message.delete()
                    await message.author.timeout(timeout_until, reason="Golden Rule")
                except discord.Forbidden:
                    await message.channel.send("I don't have permission to time out this user.")
                except Exception as e:
                    print(e)
                break


async def setup(bot):
    await bot.add_cog(automod(bot))
