import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from time import sleep
import random
from datetime import datetime
import asyncio
dotenv = load_dotenv(".env")
token = os.getenv("TOKEN")

game = discord.Game(name="StormyXV on YouTube")

bot = commands.Bot(command_prefix="$ ", intents=discord.Intents().all(), activity=game, status=discord.Status.idle, help_command=None)

@bot.event
async def on_ready():
    try:
        # Load cogs
        for filename in os.listdir("./Commands"):
            if filename.endswith(".py"):
                await bot.load_extension(f"Commands.{filename[:-3]}")
                print(f"{filename} loaded")
        # Load Task Cogs
        for filename in os.listdir("./Tasks"):
            if filename.endswith(".py"):
                await bot.load_extension(f"Tasks.{filename[:-3]}")
                print(f"{filename} loaded")
        # Load Event Cogs
        for filename in os.listdir("./Events"):
            if filename.endswith(".py"):
                await bot.load_extension(f"Events.{filename[:-3]}")
                print(f"{filename} loaded")

        # After loading extensions, set the help command if it exists
        if "help.py" in os.listdir("./Commands"):
            # Assuming your help command cog is named help in help.py
            if 'help' in bot.cogs:
                bot.help_command = bot.cogs['help']
                print("Help command set.")
            else:
                print("help cog not found in cogs.")


        # Sync commands
        synced = await bot.tree.sync()
        print("Synced " + str(len(synced)) + " commands")
        print("Logged in as " + str(bot.user.name))
    except Exception as e:
        print(e)

bot.run(token)