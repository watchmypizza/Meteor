import discord
from discord.ext import commands
import os
import dotenv
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

service = os.getenv("FIREBASE_JSON")

cred = credentials.Certificate(service)

db = firestore.client()
collection_ref = db.collection("serverconfigs")

class lscmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_guild_configs(self, current_guild_id: str):
        doc_ref = collection_ref.document(current_guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    @commands.command()
    async def ls(self, ctx):
        try:
            csi = str(ctx.guild.id)
            data = await self.get_guild_configs(csi)
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
                if not data["bot_role"] == 0:
                    if discord.utils.get(ctx.guild.roles, id=data["bot_role"]) in member.roles:
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