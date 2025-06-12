import os
import asyncio
import discord
import json
from io import BytesIO
import shutil
import re
from src.env_config import config

def build_book_cog_payload(*,user: str, title: str, author: str = "") -> dict[str,dict[str,str]]:
    """ 
    Builds specific payload for book cog api calls. 
    
    Args :
        kwargs (str): user , title , author
    Returns :
        dictionary with string keys and dictionary values
        {`unknown_book`: {`title`: ..., `author`: .. }, `user_details`: {`username`: ... }}
        
    """
    unknown_book = {
        'title' : title,
        'author' : author
    }

    user_details = {'username' :  user}

    data = {
        'unknown_book' : unknown_book,
        'user_details' : user_details
    }
    return data
def sanitize_username(username : str) -> str:
    """ removes forbidden special chars from being used in file/folder or OS related naming """
    return re.sub(r'[<>:"/\\|?*.]', '', username)

async def discord_file_creation(username : str) -> tuple[discord.File,str] | tuple[None,None]:
    ''' prevents blocking io behaviour '''
    return await asyncio.to_thread(_discord_file_creation,username)

def _discord_file_creation(username : str) -> tuple[discord.File,str] | tuple[None,None]:
    ''' Creates a file object for discord to upload '''
    
    # to be returned #
    target_file_path = None
    attached_file = None
    ##################
    target_file_ctime = 0
    discord_file_name = None

    try:

        user_folder = os.path.join(config.DOWNLOAD_DIR,username)
        if not os.path.isdir(user_folder):
            return (None , None)
        
        for item in os.listdir(user_folder):
            if item.endswith('epub'):
                item_path = os.path.join(user_folder,item)
                item_ctime = os.path.getctime(item_path)
                if item_ctime > target_file_ctime:
                    target_file_path , target_file_ctime = item_path, item_ctime
                    discord_file_name = item
        if target_file_path:
            with open(target_file_path , 'rb') as file:
                file_bytes = BytesIO(file.read())
            file_bytes.seek(0)
            attached_file = discord.File(fp=file_bytes,filename=discord_file_name)
    except Exception as e:
        print(f'discord file creation failed - {e}')

    if attached_file is not None and target_file_path is not None:
        return (attached_file , target_file_path)
    return (None, None)
async def book_search_output(username: str) -> list[dict]:
    ''' prevents blocking io behaviour'''
    return await asyncio.to_thread(_book_search_output,username)

def _book_search_output(username:str) -> list[dict]:
    ''' reads in and returns search results in a dictionary for the bot '''
    user_folder = os.path.join(config.DOWNLOAD_DIR,username)
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

def extract_response_file_name(data:dict):
    #file meta data is returned with the response can strip the .finish and then adjust the returns later 
    #response -> metadata key -> value is a dict -> we get the source key to get full path
    metadata = data.get('metadata')
    if metadata is None:
        return
    expected_finish_source = metadata.get('source')
    if expected_finish_source is None:
        return

    source_path = expected_finish_source
    end_str_flag = ".finish"
    #data is full path , strip just for full file name
    file_name = os.path.basename(source_path)
    if file_name.endswith(end_str_flag):
        return file_name[:-len(end_str_flag)] #strip the end
    return ""

if __name__ == '__main__':
    print("not meant to be ran alone")
    