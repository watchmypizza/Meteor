import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Help",
            description="Please use the `$ man <command>` feature instead.",
            color=discord.Color.red()
        )
        await self.get_destination().send(embed=embed)

async def setup(bot):
    bot.help_command = CustomHelpCommand()
