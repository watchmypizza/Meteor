import discord
from discord.ext import commands
import os
import dotenv
from firebase_admin import credentials, firestore

env = dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class kickban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

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
            data = await self.get_guild_configs(csi)
            if data["mod_logs"] != 0:
                ch = discord.utils.get(ctx.guild.channels, id=data["mod_logs"])
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