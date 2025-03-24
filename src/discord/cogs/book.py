import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands

import aiohttp
class Book(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.user_sessions = {}
    """
    getbook used with 
    we would normally split off to webserver to execute script here

    """
    @app_commands.command(name="findbook", description="Gets you a book.")
    @app_commands.describe(title="title",author="author")
    async def findbook(self,interaction: discord.Interaction, title : str, author : str):
        user_name = interaction.user.name
        await interaction.response.send_message(f'Looking for {title} by {author}')
        print(f'{title} {author}')
        print(type(interaction), type(user_name),f'{user_name}')
        print(interaction.user.name)
        await interaction.followup.send("Should be file.")
        ####
        #expected payload 
        
        unknown_book = {
            'title' : title,
            'author' : author
        }
        user_details = { 'username' : user_name}
        data = {
            'unknown_book' : unknown_book,
            'user_details' : user_details
        }
        test_url = 'http://localhost:8000/find_book'
        try:

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(test_url, json=data) as response:
                        if response.status == 200:
                            await interaction.followup.send("file")
                        else:
                            await interaction.followup.send("fail")
                except Exception as e:
                    print(f'{e}')
        except aiohttp.ClientError as e:
            print(f"A client error occurred: {e}")
        except aiohttp.ClientConnectionError as e:
            print(f"A connection error occurred: {e}")
        except aiohttp.ClientResponseError as e:
            print(f"A response error occurred: {e.status} - {e.message}")
        except aiohttp.ClientTimeout as e:
            print(f"A timeout error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        ####
        '''
        need to setup payload here with requests/response or aiotthp
        data = {title : "title", author : "author"}
        '''

async def setup(bot):
    await bot.add_cog(Book(bot))