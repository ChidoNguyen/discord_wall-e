import aiohttp

import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

from typing import Callable , Awaitable , Optional , Union

from json import JSONDecodeError
from ..utils import sanitize_username, discord_file_creation , book_search_output , tag_file_finish
from src.discord_bot.pagination import PaginatorView 

from src.env_config import config

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
                 cog : Union["Book",commands.Cog], #commands.Cog, 
                 links: list, 
                 interaction : discord.Interaction,
                 *,
                 timeout=120
                 ):
        super().__init__(timeout=timeout)
        self.links = links
        self.cog = cog
        self.interaction = interaction
        self._add_buttons()

    def generate_view_content(self):
        try:
            body='Review and pick:'
            opts = [
                f"{idx}. `Title<{data['title']}>` by `Author<{data['author']}>` [more info](<{data['link'].strip()}>)" for (idx,data) in enumerate(self.links,start=1)
            ]
            return '\n'.join([body,*opts])
        except Exception as e:
            print(e)
        
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
            cog : Union["Book" , commands.Cog], 
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

        await interaction.response.defer()
        og_resp = await interaction.original_response()
        #prevents doing too many things at once
        await self.parent_view.disable_all_buttons()

        #cancels
        if self._is_cancel():
            await self._handle_cancel(interaction,og_resp)
            return
        #everything else
        await og_resp.edit(content="<In Progress>",view=self.parent_view)
        
        pick_status = await self.cog._book_cog_post_handle(interaction,self.cog.api_routes['pick'],data_payload=[self.user_option,""],book_command_handler=self._handle_pick)
        if not pick_status:
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
    
    async def _handle_pick(self,*,interaction : discord.Interaction = None, original_response : discord.InteractionMessage = None, username : str) -> bool:
        file_status = discord_file_creation(username)
        if self.cog._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await self.parent_view.attach_file(discord_file)
            tag_file_finish(source_file_path)
            return True
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
        self.active_view : set[tuple[discord.ui.View, discord.Interaction]] = set() 
        self.cog_api_session = aiohttp.ClientSession()
        self.api = config.API_ENDPOINT
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
                await interaction.delete_original_response()
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
    def _verify_discord_file(results : tuple) -> bool:
        """ 
            Verifies the return values of _discord_file_creation()
            Expect a two value tuple - (a,b):
                a - expected to be discord.File object
                b - file path to the source file (str)
        """
        if (
            results is not None
            and isinstance(results,tuple)
            and len(results) == 2
            and isinstance(results[0],discord.File)
            and isinstance(results[1], str)
        ):
            return True
        return False
    
    """
    Cog Specific Callable Handler:
        REQUIRES 3 Arguments - interaction (discord.Interaction)
                             - original_response (disocrd.InteractionMessage)
                             - username (str and sanitized)
        RETURNS BOOL
    """
    async def _find_handle(self, * , interaction : discord.Interaction, original_response : discord.InteractionMessage, username : str) -> bool:
        file_status = discord_file_creation(username=username)
        if self._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await original_response.edit(content=f"<Finished> {interaction.user.mention}",attachments=[discord_file])
            tag_file_finish(source_file_path)
            return True
        return False
    
    async def _find_hardmode_handle(self, * , interaction : discord.Interaction ,original_response : discord.InteractionMessage, username : str) -> bool:
    #build the view to display search results + buttons
        search_results = book_search_output(username)

        if not search_results:
            await original_response.edit("Nothing found.")
            return False
        
        option_view = BookOptions(self,search_results,interaction)
        option_view_content = option_view.generate_view_content()
        await original_response.edit(content=option_view_content,view=option_view)
        return True
    
    async def _dm_request_handle(self, * ,interaction : discord.Interaction, original_response : Optional[discord.InteractionMessage] = None , username : str) -> bool:
        dm_user = interaction.user
        file_status = discord_file_creation(username)
        if self._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await dm_user.send("Is this what you wanted? Too bad if it isn't.", file = discord_file)
            tag_file_finish(source_file_path)
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
            book_command_handler : Callable[[discord.Interaction, discord.InteractionMessage,str],Awaitable[bool]],
            root_url : str = None
    ) -> bool:
        if root_url is None :
            root_url = self.api
        try:
            username = sanitize_username(interaction.user.name)
            original_response = await interaction.original_response()
            request_url = root_url + task_route
            data = self.json_payload(user=username,title = data_payload[0],author = data_payload[1])
        except Exception as e:
            print(f'before post - {e}')
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
        await original_response.edit(content=f"```Try again later... and I mean later later.```")
        return False

    async def _book_cog_get_handle(
            self,
            interaction : discord.Interaction,
            task_route : str,
            book_command_handler : Callable[...,Awaitable[bool]],
            root_url : str = None
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
            await self._book_cog_post_handle(interaction,task_route=self.api_routes['find'],data_payload=[title,author],book_command_handler=self._find_handle)
        except Exception as e:
            print(e)

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