import os
import asyncio
import discord
import json
from io import BytesIO
import shutil
import re
from src.env_config import config

DOWNLOAD_DIR = config.DOWNLOAD_DIR

def sanitize_username(username : str):
    """ removes forbidden special chars from being used in file/folder or OS related naming """
    return re.sub(r'[<>:"/\\|?*.]', '', username)

async def discord_file_creation(username : str) -> tuple[BytesIO,str]:
    ''' prevents blocking io behaviour '''
    return await asyncio.to_thread(_discord_file_creation,username)

def _discord_file_creation(username : str) -> tuple[BytesIO,str]:
    ''' Creates a file object for discord to upload '''
    
    target_file = None
    target_file_ctime = 0
    discord_file_name = None
    try:
        user_folder = os.path.join(DOWNLOAD_DIR,username)

        for item in os.listdir(user_folder):
            if item.endswith('epub'):
                item_path = os.path.join(user_folder,item)
                item_ctime = os.path.getctime(item_path)
                if item_ctime > target_file_ctime:
                    target_file , target_file_ctime = item_path, item_ctime
                    discord_file_name = item

        with open(target_file , 'rb') as file:
            file_bytes = BytesIO(file.read())
        file_bytes.seek(0)
        attached_file = discord.File(fp=file_bytes,filename=discord_file_name)
        return attached_file , target_file
    
    except Exception as e:
        print(f'discord file creation failed - {e}')
        return None , None

async def book_search_output(username: str) -> dict:
    ''' prevents blocking io behaviour'''
    return await asyncio.to_thread(_book_search_output,username)

def _book_search_output(username:str) -> dict:
    ''' reads in and returns search results in a dictionary for the bot '''
    user_folder = os.path.join(DOWNLOAD_DIR,username)
    #output.txt has results
    search_result = "results.json"
    with open(os.path.join(user_folder,search_result) , 'r') as json_file:
        return json.load(json_file)

async def tag_file_finish(filepath : str):
    ''' prevents blocking of other bot related commands '''
    return await asyncio.to_thread(_tag_file_finish,filepath)

def _tag_file_finish(filepath : str):
    """ tags file to be recognized as finished with bot operations """
    shutil.move(filepath,filepath + '.finish')
    

if __name__ == '__main__':
    print("not meant to be ran alone")
    