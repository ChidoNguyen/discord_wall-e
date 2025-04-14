import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from ..utils import discord_file_creation , book_search_output , tag_file_finish

from discord.ui import View, Button
from src.discord_bot.pagination import PaginatorView
import aiohttp
import os
import re
class BookOptions(View):
    def __init__(self, 
                 cog : commands.Cog, 
                 links: list, 
                 interaction : discord.Interaction,
                 timeout=120
                 ):
        super().__init__(timeout=timeout)
        self.links = links
        self.cog = cog
        self.interaction = interaction

        for idx,json_data in enumerate(links):
            url = json_data['link']
            new_button =ButtonEmbeddedLink(cog=self.cog,label=str(idx+1),user_option=url,parent_view = self)
            self.add_item(new_button)
        # Cancel Button #
        cancel_button = ButtonEmbeddedLink(cog=self.cog,label='X', user_option = None,parent_view=self,style=discord.ButtonStyle.danger)
        self.add_item(cancel_button)

    async def on_timeout(self):
        if self.children:
            self.clear_items()
            if self.interaction:
                og_resp = await self.interaction.original_response()
                await og_resp.edit(content='```Expired```',view=self)

    async def disable_all_buttons(self):
        for butts in self.children:
            if isinstance(butts,Button):
                butts.disabled = True

    async def attach_file(self,discord_file):
        self.clear_items()
        og_resp = await self.interaction.original_response()
        await og_resp.edit(content='<Finished>', attachments=[discord_file],view=self)

class ButtonEmbeddedLink(Button):
    def __init__(
            self,
            cog : commands.Cog, 
            label : str , 
            user_option : str ,  
            parent_view : BookOptions,
            style = discord.ButtonStyle.primary
            ):
        super().__init__(label=label, style=style)
        self.cog = cog
        self.user_option = user_option
        self.parent_view = parent_view
    
    async def cancel_pick(self,interaction: discord.Interaction, og_resp : discord.InteractionMessage):
        self.parent_view.clear_items()
        await og_resp.edit(content='```Canceled```',view=self.parent_view)
        
    async def callback(self,interaction : discord.Interaction):
        #should fire off the book request
        user_name = interaction.user.name
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name)
        await interaction.response.defer()
        og_resp = await interaction.original_response()
        ####
        await self.parent_view.disable_all_buttons()
        if self.label == 'X' and self.user_option is None:
            await self.cancel_pick(interaction,og_resp)
            return
        await og_resp.edit(content="<In Progress",view=self.parent_view)
        
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
            'find' : '/find',
            'find_hardmode' : '/find_hardmode',
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

    @app_commands.command(name="find", description="Searches for a publication.")
    @app_commands.describe(title="title",author="author")
    async def find(self,interaction: discord.Interaction, title : str, author : str):
        user_name = interaction.user.name
        #sanitize cause discord lets "." come in
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name) #just do a remove
        await interaction.response.send_message(f'Looking for \"{title} by {author}\"')
        original_message = await interaction.original_response()
        data = self.json_payload(user=user_name,title=title,author=author)
        req_url = self.api + self.api_routes['find']
        try:
            async with self.cog_api_session.post(req_url, json=data) as response:
                if response.status == 200:
                    try:
                        job_status = await response.json()
                        if job_status is not None:
                            to_be_attached, finished_file = discord_file_creation(user_name)
                            await original_message.edit(content=
                                f'{original_message.content}\n<Finished> {interaction.user.mention}',
                                attachments=[to_be_attached]
                                )
                            tag_file_finish(finished_file)
                            return
                        else:
                            print("Empty find response despite 200 response.")
                    except Exception as e:
                        print(f'find request -  Failed to parse JSON: {e}')
                else:
                    print(f'findbook non-200 response: {response.status}')
        except aiohttp.ClientError as e:
            print(f"A client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        # Update user message with error
        await original_message.edit(content="```Error: /find```")

    @app_commands.command(name='find_hardmode', description="The idk who wrote it option, or just more flexibility. Search and Pick")
    @app_commands.describe(title='title',author='author (optional)')
    async def find_hardmode(self, interaction : discord.Interaction, title : str , author : str = ""):
        user_name = interaction.user.name
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user_name)

        data = self.json_payload(user=user_name,title=title,author=author)
        req_url = self.api + self.api_routes['find_hardmode']

        await interaction.response.send_message("Working on it.")
        original_message = await interaction.original_response()
        try:
            async with self.cog_api_session.post(req_url, json=data) as response:
                if response.status == 200:
                    try:
                        job_status = await response.json()
                        if job_status is not None:
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
                            await original_message.edit(content=options_text, view=option_view)
                            return
                        else:
                            print("Empty job_status despite 200 response")
                    except Exception as e:
                        print(f'find_hardmode - failed to parse JSON: {e}')
                else:
                    print(f'find_hardmode - received non 200 response : {response.status}')
        except aiohttp.ClientError as e:
            print(f"A client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        await original_message.edit(content="```Error: /find_hardmode```")
    
    @app_commands.command(name="whisper_it_to_me" , description="ill dm you secrets")
    @app_commands.describe(what='what',who='who')
    async def direct_msg_request(self,interaction : discord.Interaction , what : str , who : str):
        user = interaction.user
        user_name = re.sub(r'[<>:"/\\|?*.]', '', user.name)
        await user.send("Just hold your horses...")
        await interaction.response.send_message(f'{what} {who}',ephemeral=True)
        data = self.json_payload(user= user_name, title= what, author= who)
        url = self.api + self.api_routes['find']
        try:
            async with self.cog_api_session.post(url,json=data) as response:
                if response.status == 200:
                    try:
                        resp_status = await response.json()
                        if resp_status is not None:
                            to_be_attached , finished_file = discord_file_creation(user_name)
                            await user.send("You wanted..." , file=to_be_attached)
                            tag_file_finish(finished_file)
                            return
                        else:
                            print("Empty job_status despite 200 response.")
                    except Exception as e:
                        print(f'whisper_in_my_ear - failed to parse JSON: {e}')
                else:
                    print(f'whisper_in_my_ear received non 200 response : {response.status}')
        except aiohttp.ClientError as e:
            print(f"A client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        await user.send("Something went wrong sorry dude.")

    @app_commands.command(name="catalog", description="do you like your finger before you turn the page?")
    async def catalog(self, interaction: discord.Interaction):
        try:
            embeds = [discord.Embed(title=f"Page {i+1}", description=f"Content {i+1}") for i in range(5)]
            view = PaginatorView(embeds)
            await interaction.response.send_message(embed=embeds[0],view=view)
        except Exception as e:
            print(e)
async def setup(bot):
    await bot.add_cog(Book(bot))