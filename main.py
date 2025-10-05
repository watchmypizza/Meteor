import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from collections import defaultdict
import asyncio

load_dotenv(".env")
token = os.getenv("TOKEN")

game = discord.Game(name="Catching Meteors")
DEFAULT_PREFIX = "$ "

async def dynamic_prefix(bot: commands.Bot, message: discord.Message):
   if message.guild is None:
       return DEFAULT_PREFIX
   gid = str(message.guild.id)
   cog = (bot.get_cog("getPrefix")
          or bot.get_cog("RefreshCache")
          or bot.get_cog("Prefix"))
   prefix = DEFAULT_PREFIX
   if cog and getattr(cog, "serverconfigcache", None) is not None:
       raw = (cog.serverconfigcache.get(gid, {}) or {}).get("prefix", DEFAULT_PREFIX)
       prefix = str(raw).strip() or DEFAULT_PREFIX
   return commands.when_mentioned_or(prefix)(bot, message)

class TuxBot(commands.Bot):
   async def setup_hook(self):
       for folder in ("Commands", "Tasks", "Events"):
           for filename in os.listdir(f"./{folder}"):
               if filename.endswith(".py"):
                   mod = f"{folder}.{filename[:-3]}"
                   if mod not in self.extensions:
                       await self.load_extension(mod)
                       print(f"{filename} loaded")

       synced = await self.tree.sync()
       print("Synced", len(synced), "commands")

intents = discord.Intents.all()
bot = TuxBot(command_prefix=dynamic_prefix,
            intents=intents,
            activity=game,
            status=discord.Status.idle,
            help_command=None)

@bot.event
async def on_ready():
   print("Logged in as", bot.user)

bot.run(token)
