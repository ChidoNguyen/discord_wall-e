import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from ..utils import sanitize_username, discord_file_creation , book_search_output , tag_file_finish

from discord.ui import View, Button
from src.discord_bot.pagination import PaginatorView 
import aiohttp
import os
class BookOptions(View):
    """
    Class : BookOptions -  Custom discord bot UI for handling interactions with search results.
    
    View generates formatted text to provide users with <author> <title> information and <link> for user to dig deeper if needed.
    Also creates buttons related to each result choice provided.

    Attributes:
        cog : commands.Cog : the discord commands Cog this view is associated with. -> main purpose to have access to the clientSession() object in parent.
        links : list :  a list of links to be handled by the view
        interaction : discord.Interaction : the discord interaction that initiated the creation of the view

    """
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
        self._add_buttons()

    def _add_buttons(self):
        """ Creates a Button for each link , and a cancel button. """
        for idx,json_data in enumerate(self.links):
            url = json_data['link']
            new_button =ButtonEmbeddedLink(
                cog=self.cog,
                label=str(idx+1),
                user_option=url,
                parent_view = self
                )
            self.add_item(new_button)

        # Cancel Button #
        cancel_button = ButtonEmbeddedLink(
            cog=self.cog,
            label='X',
              user_option = None,
              parent_view=self,
              style=discord.ButtonStyle.danger
              )
        self.add_item(cancel_button)

    async def on_timeout(self):
        if self.children:
            self.clear_items()
            if self.interaction:
                og_resp = await self.interaction.original_response()
                await og_resp.edit(content='```Expired```',view=self)

    async def disable_all_buttons(self):
        """ Deactivates button after one has been selected. """
        for butts in self.children:
            if isinstance(butts,Button):
                butts.disabled = True

    async def attach_file(self,discord_file):
        """ Attaches a file and clears all previous view items. """
        self.clear_items()
        og_resp = await self.interaction.original_response()
        await og_resp.edit(content='<Finished>', attachments=[discord_file],view=self)

class ButtonEmbeddedLink(Button):
    """
    Class - ButtonEmbeddedLink - Creates Buttons that is related to the url in BookOption view.

    Attributes:
        cog : commands.Cog the cog extension associated with view
        user_option : stores the url/link str associated with button/choice
        parent_view : the view that is invoking the creation of buttons
    """
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
    
    async def callback(self,interaction : discord.Interaction):
        #should fire off the book request
        user_name = sanitize_username(interaction.user.name)

        await interaction.response.defer()
        og_resp = await interaction.original_response()

        await self.parent_view.disable_all_buttons()

        if self._is_cancel():
            await self._handle_cancel(interaction,og_resp)
            return

        await og_resp.edit(content="<In Progress>",view=self.parent_view)
        
        pick_status = await self._handle_pick(user_name,interaction)

        if pick_status is False:
            self.parent_view.clear_items()
            await og_resp.edit(content="Pick failed verify info.",view = self.parent_view)

        return

    def _is_cancel(self) -> bool:
        """ Checks to see if its the cancel button """
        expected_label = 'X' # change to liking 
        return self.label == expected_label and self.user_option is None

    async def _handle_cancel(self , interaction : discord.Interaction , original_response : discord.InteractionMessage):
        """ Removes all buttons from view and updates message to show cancellation. """
        self.parent_view.clear_items()
        await original_response.edit(content='```Canceled```', view=self.parent_view)
    
    async def _handle_pick(self,username : str , interaction : discord.Interaction ):
        """ Process the pick-interaction executed by the user."""

        request_url = self.cog.api + self.cog.api_routes['pick']
        data = self.cog.json_payload(
            user= username,
            title= self.user_option
            )
        
        try:
            async with self.cog.cog_api_session.post(url= request_url,json= data) as response:
                job_status = await response.json()
                if response.status == 200 and job_status is not None:
                    discord_file_object , source_file = discord_file_creation(username)
                    if discord_file_object is not None and source_file is not None:
                        await self.parent_view.attach_file(discord_file_object)
                        tag_file_finish(source_file)
                        return True
                    else:
                        await interaction.followup.send("Pick failed to get file.")
                else:
                    await interaction.followup.send("Pick failed - server issue.")
        except Exception as e:
            print(f'pick error - {e}')
            return False
        
class Book(commands.Cog):
    """
    Class Book : our extension/cog - Does things I want it to do

    Attributes: 
        bot : instance of Bot that is loading cog
        cog_api_session : clientsession() 1 shared session for cog instance 
        api : address/url to API
        api_routes : dict of routes 

    """
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
            
    def json_payload(self,*, user : str , title : str , author : str = "") -> dict:
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
        user_name = sanitize_username(interaction.user.name)

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
                                f'<Finished> {interaction.user.mention}',
                                attachments=[to_be_attached]
                                )
                            tag_file_finish(finished_file)
                            return
                        else:
                            print("find - Empty find response despite 200 response.")
                            await interaction.followup.send('Issue finding requested item.',ephemeral=True)
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
        user_name = sanitize_username(interaction.user.name)
        

        data = self.json_payload(user=user_name,title=title,author=author)
        req_url = self.api + self.api_routes['find_hardmode']

        await interaction.response.send_message("Working on it...")
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
                                options_text += f"{idx}. `Title<{title}>` `Author<{author}> ` [more info](<{url.strip()}>) \n"
                            await original_message.edit(content=options_text, view=option_view)
                            return
                        else:
                            print("find_hardmode : Empty job_status despite 200 response")
                            await interaction.followup.send("No valid results were found." , ephemeral=True)
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
        user_name = sanitize_username(user.name)
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

    @app_commands.command(name="catalog", description="do you lick your finger before you turn the page?")
    async def catalog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = self.api + '/catalog'
        try:
            async with self.cog_api_session.get(url=url) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data is not None:
                        #reponse data list[list[str]]
                        page_view = PaginatorView(response_data['catalog'],interaction)
                        embeds = page_view.create_catalog_embed()
                        await interaction.followup.send(embed=embeds,view=page_view)
        except Exception as e:
            print(f'pagination of catalog error - {e}')
        return

async def setup(bot):
    await bot.add_cog(Book(bot))