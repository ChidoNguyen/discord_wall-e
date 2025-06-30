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

from src.discord_bot.utils.book_cog_util import sanitize_username, create_discord_file_attachment, extract_response_file_info , tag_file_finish

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
    
    async def _handle_book_api_command(self,*, interaction: discord.Interaction, option: str, title: str, author: str, success_callback: Callable[..., Awaitable[Any]]):
        #revisit callable hinting later
        ''' Reusable code for invoking api handler code for POST requests. '''

        username = sanitize_username(interaction.user.name)
        original_response = await interaction.original_response()
        api_response = await self.api_handler.post_to_api(title=title,author=author, username=username, option=option)

        if not api_response or api_response.get("status") != "success":
            await original_response.edit(content="A problem occurred please try again later.")
            return
        
        success_callback(username=username, api_response=api_response)


    @app_commands.command(name= "find", description= "Searches for a publication.")
    @app_commands.describe(title= "Title", author= "Author")
    async def find(self, interaction: discord.Interaction, title: str, author: str):
        async def on_find_success(username: str, api_response: dict):
            file_info = extract_response_file_info(api_response)
            if not file_info:
                print("handle error later")
                return
            file_path , file_name = file_info
            

            discord_file_obj = await create_discord_file_attachment(file_path=file_path, file_name=file_name)

            await interaction.edit_original_response(content= f"<Finished> {interaction.user.mention}", attachments=[discord_file_obj])
            await tag_file_finish(file_path=file_path)

            return

        await interaction.response.send_message(f'Looking for \"{title} by {author}\"')
        
        await self._handle_book_api_command(option="find",interaction=interaction, title=title, author=author,success_callback=on_find_success)
            