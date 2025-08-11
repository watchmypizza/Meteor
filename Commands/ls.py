import discord
from discord.ext import commands

class lscmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ls(self, ctx):
        try:
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
                if discord.utils.get(ctx.guild.roles, id=1403062164100612239) in member.roles:
                    continue
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