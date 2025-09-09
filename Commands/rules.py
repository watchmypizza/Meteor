import discord
from discord.ext import commands

class rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="postrules")
    async def postrules(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You do not have permission to use this command.")
            return
        
        embed = discord.Embed(
            description="""
            1. Be over the age of 13.
             - Not following this will result in an immediate ban with no appeal.\n
            2. Racism of any kind is not allowed
             - This also includes words that might be interpreted as racism.
             - Not following this rule will result in immediate punishment.\n
            3. Keep content child friendly
             - NSFW, Gore or any sorts of material compromising child safety is not allowed.
             - Violating this rule will result in an immediate ban.\n
            4. Stay respectful
             - Don't insult one another's feelings or bring up controversial topics. Examples of such are: Politics, religion, etc.
             - Breaking this rule will carry a punishment based off of the severity.\n
            5. English Only
             - Breaking this rule will result in a warning.\n
            6. No venting
             - We want this server to pose as an escape from the real world. We have staff members who are happy to support you in such matter.\n
            7. Swearing is OK
             - Swearing is allowed aslong it doesn't get directed to another person. We do not allow any kind of slurs here, if you can recall it or not.\n
            8. Channels should be used appropiately
             - Chat can be dead a lot of times, and that is okay! Please keep things on-topic tho.\n
            9. Don't ping excessively
             - Pinging excessively without the permission of someone else will get you punished based off of the serverity.\n
            10. Do not impersonate
             - Impersonation is not tolerated and will get you banned immediately.\n
            11. Don't use alt accounts
             - Joining this server using an alt account while your main account is in the server will get both accounts punished.\n
            
            Incase you need assistance, always feel free to open a ticket or ask for support!"""
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(rules(bot))