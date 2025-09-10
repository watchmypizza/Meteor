import discord
from discord.ext import commands
import os
import json

class kickban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"

    def read(self, current_server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        
        if current_server_id not in data:
            data[current_server_id] = {
                "logging_channel": 0,
                "welcomer_channel": 0,
                "level_roles": [],
                "staff_roles": [],
                "ann_channel": 0,
                "bot_role": 0,
                "mod_logs": 0
            }
        
        return data

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
            
            csi = str(ctx.guild.id)
            data = self.read(csi)
            if data[csi]["mod_logs"] != 0:
                ch = discord.utils.get(ctx.guild.channels, id=data[csi]["mod_logs"])
                if arg == "-rf":
                    if reason:
                        embed = discord.Embed(
                            title="Member banned",
                            description=f"{member.mention} has been banned for `{reason}` by {ctx.author.mention}",
                            color=discord.Color.red()
                        )
                    else:
                        embed = discord.Embed(
                            title="Member banned",
                            description=f"{member.mention} has been banned by {ctx.author.mention}",
                            color=discord.Color.red()
                        )
                if arg == "-r":
                    if reason:
                        embed = discord.Embed(
                                title="Member kicked",
                                description=f"{member.mention} has been kicked for `{reason}` by {ctx.author.mention}",
                                color=discord.Color.red()
                            )
                    else:
                        embed = discord.Embed(
                            title="Member kicked",
                            description=f"{member.mention} has been kicked by {ctx.author.mention}",
                            color=discord.Color.red()
                        )
                
                await ch.send(embed=embed)
            

        except discord.Forbidden:
            await ctx.send(f"I don't have the necessary permissions to {'ban' if arg == '-rf' else 'kick'} this member.")
        except discord.HTTPException as e:
            await ctx.send(f'An error occurred: {e}')

async def setup(bot):
    await bot.add_cog(kickban(bot))