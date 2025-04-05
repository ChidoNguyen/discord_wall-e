import os
import discord
import json
import shutil
from dotenv import load_dotenv

#env vars#
load_dotenv()
Download_dir = os.getenv('DOWNLOAD_DIR')

def discord_file_creation(username : str):
    #get path
    #load files
    #check c time
    #get newest file

    #obtain newest file in folder#
    user_folder = os.path.join(Download_dir,username)
    target_file = None
    target_file_ctime = 0
    discord_file_name = None
    for item in os.listdir(user_folder):
        item_path = os.path.join(user_folder,item)
        item_ctime = os.path.getctime(item_path)
        if item_ctime > target_file_ctime:
            target_file , target_file_ctime = item_path, item_ctime
            discord_file_name = item
    #####
    import io
    with open(target_file , 'rb') as file:
        file_bytes = io.BytesIO(file.read())
    file_bytes.seek(0)
    attached_file = discord.File(fp=file_bytes,filename=discord_file_name)
    #with open(target_file , 'rb') as file:
        #attached_file = discord.File(fp = file)
    #append .finish after finishing
    return attached_file , target_file

def book_search_output(username:str):
    user_folder = os.path.join(Download_dir,username)
    #output.txt has results
    search_result = "results.json"
    with open(os.path.join(user_folder,search_result) , 'r') as json_file:
        return json.load(json_file)
def tag_file_finish(filepath : str):
    shutil.move(filepath,filepath + '.finish')
    return
if __name__ == '__main__':
    print("not meant to be ran alone")
    