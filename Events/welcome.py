import discord
from discord.ext import commands

class welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title=f"Welcome, {member.name}",
            description=f"Welcome to Development Cave! {member.mention}",
            color=discord.Color.random()
        )
        url = member.avatar.url if member.avatar else str(member.default_avatar)
        embed.set_thumbnail(url=url)
        embed.set_footer(text=f"ID: {member.id}")
        
        welcome_ch = discord.utils.get(member.guild.channels, id=1392616607456563353)
        await welcome_ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(welcomer(bot))