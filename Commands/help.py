import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Help",
            description="Available commands:\n`/8ball`\n`$ cat <file>`\n`$ clear <amt>`\n`$ ls`\n`$ man <cmd>`\n`$ pwd`\n`$ rm --r(f) <user> --message <reason>`\n`/slash`\n`$ wall <msg>`\n`$ usermod -l <new nick> <user>`\n`/membercount`\n`/level (<User>)`\n`/warn <User>`\n`/warnings <User>`\n`/removewarn <User>`\n`/configure <Option>`\n`/counting <Option>`\n`/latency`",
            color=discord.Color.red()
        )
        await self.get_destination().send(embed=embed)

async def setup(bot):
    bot.help_command = CustomHelpCommand()
