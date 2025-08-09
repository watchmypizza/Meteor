import discord
from discord.ext import commands

class kickban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rm(self, ctx, arg: str, member: discord.Member, *, reason_input=None):
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send("You do not have sudo privileges to execute this command.")
            return

        if arg not in ["-r", "-rf"]:
            await ctx.send("Invalid arguments. Use `rm <user> -r(f) --message \"reason\"`")
            return

        reason = None
        if reason_input:
            reason_parts = reason_input.split(" ", 1)
            if reason_parts and reason_parts[0] == "--message":
                if len(reason_parts) > 1:
                    reason = reason_parts[1]
                else:
                    await ctx.send("Please provide a reason after --message.")
                    return
            else:
                await ctx.send("Invalid arguments. Use `rm <user> -r(f) --message \"reason\"`")
                return

        try:
            if arg == "-rf":
                if reason:
                    await member.ban(reason=f"Banned by {ctx.author} for: {reason}")
                    await ctx.send(f'{member.mention} has been banned for: {reason}')
                else:
                    await member.ban(reason=f"Banned by {ctx.author}")
                    await ctx.send(f'{member.mention} has been banned.')

            elif arg == "-r":
                if reason:
                    await member.kick(reason=f"Kicked by {ctx.author} for: {reason}")
                    await ctx.send(f'{member.mention} has been kicked for: {reason}')
                else:
                    await member.kick(reason=f"Kicked by {ctx.author}")
                    await ctx.send(f'{member.mention} has been kicked.')

        except discord.Forbidden:
            await ctx.send(f"I don't have the necessary permissions to {'ban' if arg == '-rf' else 'kick'} this member.")
        except discord.HTTPException as e:
            await ctx.send(f'An error occurred: {e}')

async def setup(bot):
    await bot.add_cog(kickban(bot))
    print("RM cog loaded.")