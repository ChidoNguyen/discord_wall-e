import discord.interactions
import discord
from discord import app_commands
from discord.ext import commands

class BotHelp(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.abilities = [
            "Book - Does book stuff.",
            "TBD - TEE BEE DEE"
        ]

    @app_commands.command(name="help" ,description="The bot reveals itself to you semi-intimately.")
    async def help(self, interaction: discord.Interaction):
        #user_name = interaction.user.name
        multi_line_response = '\n'.join(self.abilities)
        await interaction.response.send_message(multi_line_response)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Responds with Pong!"""
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

async def setup(bot):
    await bot.add_cog(BotHelp(bot))
