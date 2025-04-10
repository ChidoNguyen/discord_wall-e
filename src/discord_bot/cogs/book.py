import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from ..utils import discord_file_creation , book_search_output , tag_file_finish

from discord.ui import View, Button

import aiohttp
import os
import re
class BookOptions(View):
    def __init__(self, cog : commands.Cog, links: list, interaction : discord.Interaction):
        super().__init__()
        self.links = links
        self.cog = cog
        self.interaction = interaction

        for idx,json_data in enumerate(links):
            url = json_data['link']
            new_button =ButtonEmbeddedLink(cog=self.cog,label=str(idx+1),user_option=url,parent_view = self)
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
        await og_resp.edit(content='<Finished>', attachments=[discord_file],view=self)

class ButtonEmbeddedLink(Button):
    def __init__(self, cog : commands.Cog, label , user_option : str ,  parent_view : BookOptions):
        super().__init__(label = label, style = discord.ButtonStyle.primary)
        self.cog = cog
        self.user_option = user_option
        self.parent_view = parent_view
        
    async def callback(self,interaction : discord.Interaction):
        #should fire off the book request
        user_name = interaction.user.name
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name)
        await interaction.response.defer()
        ####
        await self.parent_view.disable_all_buttons()
        ###
        req_url = self.cog.api + self.cog.api_routes['pick']
        data = self.cog.json_payload(user=user_name,title=self.user_option)
        try:
            async with self.cog.cog_api_session.post(url=req_url,json=data) as response:
                job_status = await response.json()
                to_be_attached , finished_file = discord_file_creation(user_name)
                if response.status == 200 and job_status is not None:
                    await self.parent_view.attach_file(to_be_attached)
                    tag_file_finish(finished_file)
                else:
                    await interaction.followup.send("Pick Failed.")
        except Exception as e:
            print(e)
        ###


class Book(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.user_sessions = {}
        self.cog_api_session = aiohttp.ClientSession()
        self.api = os.getenv("API_ENDPOINT")
        self.api_routes = {
            'findbook' : '/find_book',
            'findbook_roids' : '/find_book_roids',
            'pick' : '/pick'
        }
    async def cog_unload(self):
        try:
            await self.cog_api_session.close()
        except Exception as e:
            print(f'Failed to close out client session for book extension - {e}')
        finally:
            print('Book unloaded.')
            
    def json_payload(self,*, user : str , title : str , author : str = ""):
        unknown_book = {
            'title' : title,
            'author' : author
        }
        user_details = { 'username' : user}
        
        data = {
            'unknown_book' : unknown_book,
            'user_details' : user_details
        }

        return data

    @app_commands.command(name="findbook", description="Gets you a book.")
    @app_commands.describe(title="title",author="author")
    async def findbook(self,interaction: discord.Interaction, title : str, author : str):
        user_name = interaction.user.name
        #sanitize cause discord lets "." come in
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name) #just do a remove
        await interaction.response.send_message(f'Looking for {title} by {author}')
        data = self.json_payload(user=user_name,title=title,author=author)
        req_url = self.api + self.api_routes['findbook']
        bot_command_status = False
        try:
            async with self.cog_api_session.post(req_url, json=data) as response:
                try:
                    job_status = await response.json()
                    if response.status == 200 and job_status is not None:
                        bot_command_status = True
                        to_be_attached, finished_file = discord_file_creation(user_name)
                        original_message = await interaction.original_response()
                        await original_message.edit(content=
                            f'{original_message.content}\n<Finished> {interaction.user.mention}',
                            attachments=[to_be_attached]
                            )
                        tag_file_finish(finished_file)
                    else:
                        print(response)
                except Exception as e:
                    print(f'findbook -  {e}')
                    #await interaction.followup.send("file",file=to_be_attached)
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
        finally:
            if bot_command_status is False:
                await interaction.followup.send("```Error: /findbook```")

    @app_commands.command(name='findbook_on_roids', description="The idk who wrote it option, or just more flexibility. Search and Pick")
    @app_commands.describe(title='title',author='author (optional)')
    async def findbook_on_roids(self, interaction : discord.Interaction, title : str , author : str = ""):
        user_name = interaction.user.name
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name)
        data = self.json_payload(user=user_name,title=title,author=author)
        req_url = self.api + self.api_routes['findbook_roids']

        await interaction.response.send_message("Working on it.")
        try:
            async with self.cog_api_session.post(req_url, json=data) as response:
                job_status = await response.json()
                if response.status == 200 and job_status is not None:
                    search_results = book_search_output(user_name)
                    option_view = BookOptions(self,search_results,interaction)
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
    
    @app_commands.command(name="whisper_in_your_ear" , description="ill dm you secrets")
    @app_commands.describe(what='what',who='who')
    async def book_dm(self,interaction : discord.Interaction , what : str , who : str):
        user = interaction.user
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user.name)
        await user.send("Just hold your horses...")
        await interaction.response.send_message(f'{what} {who}',ephemeral=True)
        data = self.json_payload(user= user_name, title= what, author= who)
        url = self.api + self.api_routes['findbook']
        try:
            async with self.cog_api_session.post(url,json=data) as response:
                resp_status = await response.json()
                if response.status == 200 and resp_status is not None:
                    to_be_attached = discord_file_creation(user_name)
                    await user.send("You wanted..." , file=to_be_attached)
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