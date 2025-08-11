import discord
from discord.ext import commands

class manual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def man(self, ctx, *, command):
        match command:
            case "8ball": 
                await ctx.send("`/8ball <Question>` Gives you a random answer for a question.")
            case "cat": 
                await ctx.send("`$ cat <File>` Display any file the bot uses. Though there is an exclusion list, don't be stupid.")
            case "clear": 
                await ctx.send("`$ clear <Amount>` Clears an amount of specified messages in the current channel.")
            case "ls": 
                await ctx.send("`$ ls` Display server information.")
            case "man": 
                await ctx.send("`$ man <Command>` Command to give a manual for a command.")
            case "pwd":
                await ctx.send("`$ pwd` Returns the current path the bot is running in.")
            case "rm":
                await ctx.send("`$ rm --r(f) <User> --message <Reason>` Admin command to ban / kick members.")
            case "slash":
                await ctx.send("`/slash` For the active developer badge, as this bot focuses on Chat-Commands")
            case "wall":
                await ctx.send("`$ wall <Message>` Post something into the announcements channel, in the linux broadcast style.")
            case "usermod":
                await ctx.send("`$ usermod -l <New Nickname> <User>` Change a user's nickname.")
            case "membercount":
                await ctx.send("`/membercount` Display the amount of members in the server.")
            case "level":
                await ctx.send("`/level <(Optional) User>` Display a user's level and xp or your own level and xp.")

async def setup(bot):
    await bot.add_cog(manual(bot))
    print("MAN cog loaded.")