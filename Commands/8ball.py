import discord
from discord.ext import commands
import random

class _8ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.app_commands.command(name="8ball", description="Ask 8ball")
    @discord.app_commands.describe(question='Ask the 8ball a question.')
    async def eightball(self, interaction: discord.Interaction, question: str):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        await interaction.response.send_message(f"Question: `{question}`\nAnswer: `{random.choice(responses)}`",
                                                ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(_8ball(bot))
