import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
dotenv = load_dotenv(".env")
token = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="$ ", intents=discord.Intents().all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print("Synced " + str(len(synced)) + " commands")
        print("Logged in as " + str(bot.user.name))
    except Exception as e:
        print(e)

@bot.tree.command(name="slash")
async def slash(interaction: discord.Interaction):
    await interaction.response.send_message("Hello World!", ephemeral=True)
    return

@bot.command()
async def rm(ctx, arg: str, member: discord.Member, *, reason_input=None):
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

@bot.command()
async def clear(ctx, amt: int = None):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You do not have sudo privileges to execute this command.")
        return

    if amt is None:
        await ctx.send("Invalid arguments. Use `clear <amount>`")
        return

    limit = amt

    try:
        deleted = await ctx.channel.purge(limit=limit, before=ctx.message)

        cleared_count = len(deleted)

        if cleared_count == 0:
            await ctx.send("No messages cleared.")
        elif cleared_count == 1:
            await ctx.send("Cleared `1` message.")
        else:
            await ctx.send(f"Cleared `{cleared_count}` messages.")

    except discord.Forbidden:
        await ctx.send("I don't have the necessary permissions to delete messages.")
    except discord.HTTPException as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command()
async def ls(ctx):
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

@bot.command()
async def wall(ctx, arg: str=None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have sudo privileges to execute this command.")
        return

    if arg is None:
        await ctx.send("Invalid arguments. Use `wall <message>`")
    
    ch = discord.utils.get(ctx.guild.text_channels, id=1392619508283347177)
    cur_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    await ch.send(f"""```
    Broadcast message from root@{ctx.author.name} ({cur_time}):
    
    {arg}```""")

bot.run(token)