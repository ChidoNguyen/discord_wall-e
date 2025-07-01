import os
import asyncio
import json
from src.discord_bot.utils.book_cog_api_util import BookApiClient
from src.discord_bot.utils.book_cog_util import build_book_cog_payload


## class specific usages
import aiohttp

from io import BytesIO

import discord
import discord.interactions
from discord.ext import commands
from discord import app_commands

from dataclasses import asdict

from typing import Callable, Awaitable, Any

from src.discord_bot.utils.book_cog_util import sanitize_username, create_discord_file_attachment, extract_response_file_info , tag_file_finish , book_search_output

from src.discord_bot.views.book_options import BookOptions

from src.discord_bot.models.book_models import BookCogPayload,UserDetails,SearchQuery

from env_config import config
'''
Need to clean up "Book" cog class for better encap/modular/de-coupling 
'''
class Book(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        self.api_session = aiohttp.ClientSession()
        self.api_handler = BookApiClient(
            base_url= config.API_ENDPOINT,
            api_session= self.api_session
        )

        self.active_view : set[tuple[discord.ui.View, discord.Interaction]] = set() 

    async def _handle_book_api_command(self,*, interaction: discord.Interaction, option: str, title: str, author: str, success_callback: Callable[..., Awaitable[Any]]):
        #revisit callable hinting later
        ''' Reusable code for invoking api handler code for POST requests. '''

        username = sanitize_username(interaction.user.name)
        original_response = await interaction.original_response()
        api_response = await self.api_handler.post_to_api(title=title,author=author, username=username, option=option)

        if not api_response or api_response.get("status") != "success":
            await original_response.edit(content="A problem occurred please try again later.")
            return
        
        app_command_process_status = await success_callback(username=username, api_response=api_response)
        if not app_command_process_status:
            print("deal with discord related file io error later")

    async def on_find_success(self,*,username: str, api_response: dict, interaction: discord.Interaction):
        """ Handles post API responses that requires file attachments or uploads. """
        file_info = extract_response_file_info(api_response)
        if not file_info:
            return False, "Error verifying/locating file info from API response."
        
        file_path , file_name = file_info #maybe dict change later?
        discord_file_obj = await create_discord_file_attachment(file_path=file_path, file_name=file_name)

        await interaction.edit_original_response(content= f"<Finished> {interaction.user.mention}", attachments=[discord_file_obj])

        await tag_file_finish(file_path=file_path)

        return True


    @app_commands.command(name= "find", description= "Searches for a publication.")
    @app_commands.describe(title= "Title", author= "Author")
    async def find(self, interaction: discord.Interaction, title: str, author: str):

        await interaction.response.send_message(f'Looking for \"{title} by {author}\"')
        
        await self._handle_book_api_command(option="find",interaction=interaction, title=title, author=author,success_callback= self.on_find_success)
            
    @app_commands.command(name='find_hardmode', description="The idk who wrote it option, or just more flexibility. Search and Pick")
    @app_commands.describe(title='title',author='author (optional)')
    async def find_hardmode(self, interaction : discord.Interaction, title : str , author : str = ""):
        async def on_find_hardmode_success(username: str, api_response: dict) :
            """ Grab results.json from user folder and format into options view for choosing. """
            search_result = await book_search_output(username)
            if not search_result:
                return False, "No search results were found."
            
            option_view = BookOptions(links=search_result,on_option_click=self._handle_book_api_command, success_callback= self.on_find_success)
            option_view_content = option_view.build_option_message_view()

            self.active_view.add((option_view,interaction))
            await interaction.edit_original_response(content=option_view_content, view=option_view)

            return True

        await interaction.response.send_message("Working on it...")
        await self._handle_book_api_command(option="find_hardmode",interaction=interaction,title=title,author=author,success_callback=on_find_hardmode_success)

        pass