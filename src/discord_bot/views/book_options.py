from typing import TYPE_CHECKING

import aiohttp
import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

from typing import Callable
#utils
from src.discord_bot.utils.book_cog_util import discord_file_creation, tag_file_finish
#prevents circular import since this is only suppose to be coupled with book_cogs
if TYPE_CHECKING:
    from src.discord_bot.cogs.book import Book


class BookButton(Button):
    def __init__(self, label: str, user_option: str | None, on_click: Callable | None, on_success: Callable | None, style= discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)
        self.user_option = user_option
        self.on_click = on_click
        self.on_success = on_success
    
    def _is_cancel(self):
        """ If label is `X` or if no options set treat as cancel button. """
        return self.label == "X" or not self.user_option or self.on_click is None or self.on_success is None
    
    async def callback(self, interaction: discord.Interaction):
        """ callable function passed down from parent cog to handle HTTP request in accordance to button option choice value. """
        
        #defer to check for button type first

        await interaction.response.defer()
        original_response = await interaction.original_response()

        #check button type#
        if self._is_cancel() and self.view:
            self.view.clear_items()
            await original_response.edit(content="```Cancelled```",view=self.view)
            return
        
        #on click should be api_handler
        #on success is on success call back
        if self.on_click and self.on_success:
            await self.on_click(interaction= interaction, option="pick", title=self.user_option, success_callback = self.on_success)


#cogs pass down the call back handler function?
class BookOptions(View):
    def __init__(self,*, links: list, on_option_click, success_callback, timeout=120):
        super().__init__(timeout=timeout)
        self.links=links
        self.on_option_click = on_option_click
        self.on_success = success_callback
        self._create_buttons()
        self.message: discord.Message | None
        #add buttons
    
    async def on_timeout(self):
        if not self.children:
            return
        self.clear_items()
        if self.message:
            await self.message.edit(content='```Expired```',view=self)
        

    def _create_buttons(self):
        for (index, data) in enumerate(self.links, start= 1):
            new_button = BookButton(
                label= str(index),
                user_option=data['link'],
                on_click=self.on_option_click,
                on_success = self.on_success
            )
            self.add_item(new_button)
            
        #cancel button
        self.add_item(BookButton(
            label="X",
            user_option= None,
            on_click= None,
            on_success= None
        ))

    def _generate_option_message_text(self) ->list[str]:
        """ create a text string per item to display. """
        # 1. Title by Author [more info] generic style
        return [f"{idx}. `Title<{data['title']}>` by `Author<{data['author']}>` [more info](<{data['link'].strip()}>)" for (idx,data) in enumerate(self.links,start=1) ]

    def build_option_message_view(self):
        """ Builds formatted text string to cleanly show options from user requests. """
        title_text='Review and pick:'
        try:
            options_text = self._generate_option_message_text()
            return '\n'.join([title_text,*options_text])
        except Exception as e:
            print(e)
            pass

    
class __BookOptions(View):
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
                 cog : "Book", #commands.Cog, 
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
        """ Generates and formats text string for bot to display as the book options view. """
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
        for idx,json_data in enumerate(self.links,start=1):
            url = json_data['link']
            new_button =ButtonEmbeddedLink(
                cog=self.cog,
                label=str(idx),
                user_option=url,
                parent_view = self
                )
            self.add_item(new_button)

        # Cancel Button #
        cancel_button = ButtonEmbeddedLink(
            cog=self.cog,
            label='X',
              user_option = "",
              parent_view=self,
              style=discord.ButtonStyle.danger
              )
        self.add_item(cancel_button)

    async def on_timeout(self):
        """ clears everything """
        if not self.children:
            return
        
        self.clear_items()
        try:
            if self.interaction:
                og_resp = await self.interaction.original_response()
                await og_resp.edit(content='```Expired```',view=self)
        except Exception as e:
            print(f"place holder till logging decided {e}")

    def disable_all_buttons(self):
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
            cog : "Book", #change if you feel like changing cog name
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
        self.parent_view.disable_all_buttons()

        #cancels
        if self._is_cancel():
            await self._handle_cancel(interaction,og_resp)
            return
        #everything else
        await og_resp.edit(content="<In Progress>",view=self.parent_view)
        
        pick_status = await self.cog._book_cog_post_handle(
            interaction,self.cog.api_routes['pick'],
            data_payload=[self.user_option,""],book_command_handler=self._handle_pick
            )
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
        self.parent_view.stop() # maybe?
    
    async def _handle_pick(self,*,interaction : discord.Interaction |None = None, original_response : discord.InteractionMessage | None = None, username : str) -> bool:
        file_status = await discord_file_creation(username)
        if self.cog._verify_discord_file(file_status):
            discord_file , source_file_path = file_status
            await self.parent_view.attach_file(discord_file)
            await tag_file_finish(source_file_path)
            return True
        return False
