import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands

class Book(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.user_sessions = {}
    """
    getbook used with 
    we would normally split off to webserver to execute script here

    """
    @app_commands.command(name="getbook", description="Gets you a book.")
    @app_commands.describe(title="title",author="author")
    async def getbook(self,interaction: discord.Interaction, title : str, author : str):
        user_name = interaction.user
        await interaction.response.send_message("Working on it.")
        print(f'{title} {author}')

async def setup(bot):
    await bot.add_cog(Book(bot))