import discord
from discord.ext import commands
import os, json

class lscmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = "JSONS/serverconfigs.json"
    
    def read(self, current_server_id):
        if not os.path.exists(self.config) or os.path.getsize(self.config) == 0:
            data = {}
        else:
            with open(self.config, "r") as f:
                data = json.load(f)
        
        if not current_server_id in data:
            data = {
                "bot_role": 0
            }
        if "bot_role" not in data[current_server_id]:
            data[current_server_id]["bot_role"] = 0
        
        return data

    @commands.command()
    async def ls(self, ctx):
        try:
            csi = str(ctx.guild.id)
            data = self.read(csi)
            embed = discord.Embed(
                title=ctx.guild.name,
                color=discord.Color.random()
            )
            if ctx.guild.icon.url:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            else:
                embed.set_thumbnail(url=discord.DefaultAvatar.url)
            embed.add_field(name="Description", value=f"{ctx.guild.description}", inline=True)
            embed.add_field(name="Owner", value=f"{ctx.guild.owner.mention}", inline=True)
            total_members = 0
            for member in ctx.guild.members:
                if not data[csi]["bot_role"] == 0:
                    if discord.utils.get(ctx.guild.roles, id=data[csi]["bot_role"]) in member.roles:
                        continue
                else:
                    pass
                total_members += 1
            embed.add_field(name="Member Count", value=f"{total_members}", inline=True)
            embed.add_field(name="Channels", value=f"{len(ctx.guild.channels)}", inline=True)
            embed.add_field(name="Roles", value=f"{len(ctx.guild.roles)}", inline=True)
            total_messages = 0
            for channel in ctx.guild.text_channels:
                async for message in channel.history(limit=None):
                    total_messages += 1
            embed.add_field(name="Messages sent", value=f"{total_messages}", inline=True)
            created = ctx.guild.created_at.strftime("%Y • %m • %d")
            embed.set_footer(text=f"ID: {ctx.guild.id} | Created: {created}")
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
    
async def setup(bot):
    await bot.add_cog(lscmd(bot))