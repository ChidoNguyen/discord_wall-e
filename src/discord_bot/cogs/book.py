import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from ..utils import discord_file_creation , book_search_output

from discord.ui import View, Button

import aiohttp
import os
class BookOptions(View):
    def __init__(self, links: list , interaction : discord.Interaction):
        super().__init__()
        self.links = links
        self.interaction = interaction

        for idx,json_data in enumerate(links):
            url = json_data['link']
            new_button =ButtonEmbeddedLink(label=str(idx+1),user_option=url,parent_view = self)
            self.add_item(new_button)

    async def disable_all_buttons(self):
        for butts in self.children:
            if isinstance(butts,Button):
                butts.disabled = True
        og_resp = await self.interaction.original_response()
        await og_resp.edit(content = '<In progress>',view=self)

    async def attach_file(self,discord_file):
        self.clear_items()
        og_resp = await self.interaction.original_response()
        await og_resp.edit(content='<Finished>', attachments=[discord_file])

class ButtonEmbeddedLink(Button):
    def __init__(self , label , user_option : str ,  parent_view : BookOptions):
        super().__init__(label = label, style = discord.ButtonStyle.primary)
        self.user_option = user_option
        self.parent_view = parent_view
        
    async def callback(self,interaction : discord.Interaction):
        #should fire off the book request
        user_name = interaction.user.name
        unknown_book = {
            'title' : self.user_option,
            'author' : None
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
                        if response.status == 200 and job_status is not None:
                            await self.parent_view.attach_file(to_be_attached)

                            #await interaction.followup.send(f'<finished>', file=to_be_attached)
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
        self.api = os.getenv("API_ENDPOINT")
        self.api_routes = {
            'findbook' : '/find_book',
            'findbook_roids' : '/find_book_roids'
        }
    """
    getbook used with 
    we would normally split off to webserver to execute script here

    """
    @app_commands.command(name="findbook", description="Gets you a book.")
    @app_commands.describe(title="title",author="author")
    async def findbook(self,interaction: discord.Interaction, title : str, author : str):
        user_name = interaction.user.name
        await interaction.response.send_message(f'Looking for {title} by {author}')
 
        unknown_book = {
            'title' : title,
            'author' : author
        }
        user_details = { 'username' : user_name}
        data = {
            'unknown_book' : unknown_book,
            'user_details' : user_details
        }
        req_url = self.api + self.api_routes['findbook']

        try:

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(req_url, json=data) as response:
                        job_status = await response.json()
                        if response.status == 200 and job_status is not None:
                            to_be_attached = discord_file_creation(user_name)
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

    @app_commands.command(name='findbook_on_roids', description="The idk who wrote it option, or just more flexibility. Search and Pick")
    @app_commands.describe(title='title',author='author (optional)')
    async def findbook_on_roids(self, interaction : discord.Interaction, title : str , author : str = ""):
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
        req_url = self.api + self.api_routes['findbook_roids']
        #test_url = 'http://localhost:8000/find_book_roids'
        await interaction.response.send_message("Working on it.")
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(req_url, json=data) as response:
                        job_status = await response.json()
                        if response.status == 200 and job_status is not None:
                            search_results = book_search_output(user_name)
                            option_view = BookOptions(search_results,interaction)
                            ##### want to edit original interaction ###
                            options_text = "Review and pick:\n"
                            for (idx,json_data) in enumerate(search_results,start = 1):
                                #link/author/title in json data
                                url = json_data['link']
                                author = json_data['author']
                                title = json_data['title']
                                options_text += f"{idx}. `Title<{title}>` `Author<{author}>` [more](<{url.strip()}>).\n"
                            og_response = await interaction.original_response()
                            await og_response.edit(content=options_text, view=option_view)
                            #####
                            #await interaction.followup.send("test",view = option_view)
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