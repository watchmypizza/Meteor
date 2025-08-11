import discord
from discord.ext import commands
import humanfriendly
from datetime import datetime
from datetime import timedelta
import json

class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fp = "JSONS/forbidden_words.json"
        self.forbidden = self.read()
    
    def read(self):
        try:
            with open(self.fp, "r") as f:
                data = json.load(f)
                return data.get("forbidden_words", [])
        except FileNotFoundError:
            print(f"Error: {filename} not found. Automod will not use forbidden words.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filename}. Please check the file format.")
            return []
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for word in self.forbidden:
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