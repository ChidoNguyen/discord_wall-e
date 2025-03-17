import discord
from discord.ext import commands
from discord import app_commands

class Book(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Responds with Pong!"""
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

async def setup(bot):
    await bot.add_cog(Book(bot))