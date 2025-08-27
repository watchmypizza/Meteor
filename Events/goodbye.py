import discord
from discord.ext import commands
from discord import app_commands

class goodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = discord.utils.get(member.guild.channels, id=1392616607456563353)
        embed = discord.Embed(
            title="Goodbye!",
            description="Goodbye {}, we hope to see you again!".format(member.mention),
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar.url is not None else member.default_avatar.url)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(goodbye(bot))
