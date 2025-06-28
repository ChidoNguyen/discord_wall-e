import aiohttp

import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

from typing import Callable , Awaitable , Optional , TypeGuard , Protocol
'''
Type guard to help with pylance static type hinting
Protocol to use kwarg in function handler signature
'''

from json import JSONDecodeError
#util
from src.discord_bot.utils.book_cog_api_util import BookApiClient
from src.discord_bot.utils.book_cog_util import sanitize_username, build_book_cog_payload, discord_file_creation
from ..util import sanitize_username, discord_file_creation , book_search_output , tag_file_finish
#views
from src.discord_bot.views.pagination import PaginatorView 
from src.discord_bot.views.book_options import ButtonEmbeddedLink,BookOptions
#config
from src.env_config import config

        
class BookCommandHandler(Protocol):
    ''' Needed for kwarg usage with our generic function post request handler '''
    def __call__(
            self,
            *,
            interaction : discord.Interaction,
            original_response : discord.InteractionMessage,
            username : str
    ) -> Awaitable[bool]:
        ...
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
        self.active_view : set[tuple[discord.ui.View, discord.Interaction]] = set() 
        self.cog_api_session = aiohttp.ClientSession()
        self.api = config.API_ENDPOINT
        self.api_handler = BookApiClient(
            base_url= config.API_ENDPOINT, 
            api_session= self.cog_api_session
            )
        self.api_routes = {
            'find' : '/find',
            'find_hardmode' : '/find_hardmode',
            'pick' : '/pick',
            'catalog' : '/catalog',
            'dm' : '/whisperfind'
        }

    async def cog_unload(self):
        try:
            await self.cog_api_session.close()
            for (view,interaction) in self.active_view:
                view.stop()
                if isinstance(view,PaginatorView):
                    await interaction.delete_original_response()
                else:
                    await interaction.edit_original_response(content='-',view=None)
                #await (await interact.original_response()).edit(content='X',view=None,embed=None)
        except Exception as e:
            print(f'Failed to close out client session for book extension - {e}')
    

    @staticmethod
    def json_payload(*, user : str , title : str , author : str = "") -> dict:
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

#######
    @staticmethod
    def _verify_discord_file(results : tuple[discord.File | None, str | None]) -> TypeGuard[tuple[discord.File,str]]:
        """ 
            Verifies the return values of _discord_file_creation()
            Expect a two value tuple - (a,b):
                a - expected to be discord.File object
                b - file path to the source file (str)
        """
        return results[0] is not None and results[1] is not None

    
    """
    Cog Specific Callable Handler:
        REQUIRES 3 Arguments - interaction (discord.Interaction)
                             - original_response (disocrd.InteractionMessage)
                             - username (str and sanitized)
        RETURNS BOOL
    """
    async def _find_handle(self, * , interaction : discord.Interaction, original_response : discord.InteractionMessage, username : str) -> bool:
        file_status = await discord_file_creation(username=username)
        if self._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await original_response.edit(content=f"<Finished> {interaction.user.mention}",attachments=[discord_file])
            await tag_file_finish(source_file_path)
            return True
        return False
    
    async def _find_hardmode_handle(self, * , interaction : discord.Interaction ,original_response : discord.InteractionMessage, username : str) -> bool:
    #build the view to display search results + buttons
        search_results = await book_search_output(username)

        if not search_results:
            await original_response.edit(content="Nothing found.")
            return False
        
        option_view = BookOptions(self,search_results,interaction)
        option_view_content = option_view.generate_view_content()
        self.active_view.add((option_view,interaction))
        await original_response.edit(content=option_view_content,view=option_view)
        return True
    
    async def _dm_request_handle(self, * ,interaction : discord.Interaction, original_response : Optional[discord.InteractionMessage] = None , username : str) -> bool:
        dm_user = interaction.user
        file_status = await discord_file_creation(username)
        if self._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await dm_user.send("Is this what you wanted? Too bad if it isn't.", file = discord_file)
            await tag_file_finish(source_file_path)
            return True
        return False

    async def _catalog_handle(self, interaction : discord.Interaction, data : dict) ->bool:
        try:
            data = data['catalog'] # key/value specific to our needs
            catalog = PaginatorView(data,interaction) #parent view obj
            #### REGISTER VIEW?
            self.active_view.add((catalog,interaction))
            embeds = catalog.create_catalog_embed() #create first home view
            await interaction.followup.send(embed=embeds,view=catalog)
            return True
        except Exception as e:
            print(f"Catalog init error - {e}")
            return False


    async def _book_cog_post_handle(
            self,
            interaction : discord.Interaction,
            task_route : str,
            data_payload : list,
            book_command_handler : BookCommandHandler,
            root_url : str | None = None
    ) -> bool:
        if root_url is None :
            root_url = self.api

        username = sanitize_username(interaction.user.name)
        original_response = await interaction.original_response()
        request_url = root_url + task_route
        data = self.json_payload(user=username,title = data_payload[0],author = data_payload[1])
        try:
            async with self.cog_api_session.post(request_url,json=data) as response :
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        if response_data is not None and await book_command_handler(interaction=interaction,original_response=original_response,username=username):
                                return True
                    except JSONDecodeError:
                        print(f'Error decoding response json - {task_route}')
        except aiohttp.ClientError as e:
            print(f"A client error occurred - {task_route}: {e}")
        except Exception as e:
            print(f"An unexpected error occured - {task_route}: {e}")
        await original_response.edit(content="```Try again later... and I mean later later.```")
        return False

    async def _book_cog_get_handle(
            self,
            interaction : discord.Interaction,
            task_route : str,
            book_command_handler : Callable[...,Awaitable[bool]],
            root_url : str | None = None
    ) -> bool:
        if not root_url:
            root_url = self.api
        request_url = root_url + task_route
        try:
            async with self.cog_api_session.get(url=request_url) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data is not None and await book_command_handler(interaction,response_data):
                        return True
        except Exception as e:
            print(f" task route : {task_route} error - {e}")
        return False

    @app_commands.command(name="find", description="Searches for a publication.")
    @app_commands.describe(title="title",author="author")
    async def find(self,interaction: discord.Interaction, title : str, author : str):
        try:
            await interaction.response.send_message(f'Looking for \"{title} by {author}\"')
        except Exception as e:
            print(e)
        # new approach should flatten out the logic layering with same level function calls rather than calls within calls.
        try:
            # pre request requirements : payload and sanitation work
            # api request
            # response verification
            # post processing for users

            #prep work
            username = sanitize_username(interaction.user.name)
            api_response = await self.api_handler.post_to_api(title=title,author=author,username=username,option='find')
            if not api_response:
                print("fail holder")
            print("discord file attachment")
        except Exception as e:
            print(e)
        """
        async def on_find_success(username: str, api_response: dict):
            file_info = extract_response_file_info(api_response)
            if not file_info:
                print("handle error later")
                return
            containing_folder , file_name = file_info
            #verify folder and file later
            print("invoke some verification later")
            
            ####

            with open(os.path.join(containing_folder,file_name), 'rb') as file:
                file_bytes = BytesIO(file.read())
            file_bytes.seek(0) # set back to beginning
            discord_file_object = discord.File(fp=file_bytes,filename=file_name)

            print("we'd edit original message to attach file here")
            return
        await interaction.response.send_message(f'Looking for \"{title} by {author}\"')
        
        await self._handle_book_api_command(option="find",interaction=interaction, title=title, author=author,success_callback=on_find_success)
        """
        

    @app_commands.command(name='find_hardmode', description="The idk who wrote it option, or just more flexibility. Search and Pick")
    @app_commands.describe(title='title',author='author (optional)')
    async def find_hardmode(self, interaction : discord.Interaction, title : str , author : str = ""):
        await interaction.response.send_message("Working on it...")
        await self._book_cog_post_handle(interaction,task_route=self.api_routes['find_hardmode'],data_payload=[title,author],book_command_handler=self._find_hardmode_handle)
       
    
    @app_commands.command(name="whisper_it_to_me" , description="ill dm you secrets")
    @app_commands.describe(what='what',who='who')
    async def direct_msg_request(self,interaction : discord.Interaction , what : str , who : str):
        user = interaction.user
        await user.send("Just hold your horses...")
        await interaction.response.send_message(f'{what} {who}',ephemeral=True)
        status = await self._book_cog_post_handle(interaction,task_route=self.api_routes['dm'],data_payload=[what,who],book_command_handler = self._dm_request_handle)
        
        if not status : 
            await user.send("Something went wrong sorry dude.")

    @app_commands.command(name="catalog", description="do you lick your finger before you turn the page?")
    async def catalog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not await self._book_cog_get_handle(interaction=interaction,task_route=self.api_routes['catalog'],book_command_handler=self._catalog_handle):
            await interaction.followup.send("Catalog got burnt.")
        

async def setup(bot):
    await bot.add_cog(Book(bot))