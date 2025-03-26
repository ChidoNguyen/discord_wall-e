import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from ..utils import discord_file_creation , book_search_output

from discord.ui import View, Button

import aiohttp

class BookOptions(View):
    def __init__(self, links: list , interaction : discord.Interaction):
        super().__init__()
        self.links = links
        self.interaction = interaction

        for idx,url in enumerate(links):
            new_button =ButtonEmbeddedLink(label=str(idx+1),user_option=url,parent_view = self)
            self.add_item(new_button)

    async def disable_all_buttons(self):
        for butts in self.children:
            if isinstance(butts,Button):
                butts.disabled = True
        await self.interaction.response.edit_message(view=self)

class ButtonEmbeddedLink(Button):
    def __init__(self , label , user_option : str ,  parent_view : BookOptions):
        super().__init__(label = label, style = discord.ButtonStyle.primary)
        self.user_option = user_option
        self.parent_view = parent_view

    async def callback(self,interaction : discord.Interaction):
        #should fire off the book request
        print("clicked")
        user_name = interaction.user.name
        unknown_book = {
            'title' : self.user_option,
            'author' : self.user_option
        }
        user_details = { 'username' : user_name}
        data = {
            'unknown_book' : unknown_book,
            'user_details' : user_details
        }
        test_url = "http://localhost:8000/pick"
        await interaction.response.defer()
        ####
        await self.parent_view.disable_all_buttons()
        ###
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url=test_url, json= data) as response:
                        job_status = await response.json()
                        to_be_attached = discord_file_creation(user_name)
                        if response.status == 200:
                            await interaction.followup.send(f'<finished>', file=to_be_attached)
                        else:
                            await interaction.followup.send("fail")
                except Exception as e:
                    print(f'{e}')
        except Exception as e:
            print(f'{e}')

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
        #print(f'{title} {author}')
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
                        job_status = await response.json()
                        if response.status == 200 and job_status is not None:
                            to_be_attached = discord_file_creation(username = user_name, title = title,author = author)
                            original_message = await interaction.original_response()
                            await original_message.edit(content=
                                f'{original_message.content}\n<Finished> {interaction.user.mention}',
                                attachments=[to_be_attached]
                                )
                            #await interaction.followup.send("file",file=to_be_attached)
                        else:
                            await interaction.followup.send("Failed to fetch file.")
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

    @app_commands.command(name='findbook_on_roids', description="Same as find books, but gives you some options for books to pick from.")
    @app_commands.describe(title='title',author='author')
    async def findbook_on_roids(self, interaction : discord.Interaction, title : str , author : str):
        user_name = interaction.user.name
        unknown_book = {
            'title' : title,
            'author' : author
        }
        user_details = { 'username' : interaction.user.name}
        data = {
            'unknown_book' : unknown_book,
            'user_details' : user_details
        }
        test_url = 'http://localhost:8000/find_book_roids'
        await interaction.response.send_message("Working on it.")
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(test_url, json=data) as response:
                        job_status = await response.json()
                        if response.status == 200 and job_status is not None:
                            search_results = book_search_output(user_name)
                            option_view = BookOptions(search_results,interaction)
                            await interaction.followup.send("test",view = option_view)
                        else:
                            await interaction.followup.send("Failed to fetch file.")
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
        return
    
async def setup(bot):
    await bot.add_cog(Book(bot))