import os
import discord
import json
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
    for item in os.listdir(user_folder):
        item_path = os.path.join(user_folder,item)
        item_ctime = os.path.getctime(item_path)
        if item_ctime > target_file_ctime:
            target_file , target_file_ctime = item_path, item_ctime
    #####
    with open(target_file , 'rb') as file:
        attached_file = discord.File(fp = file)
    return attached_file

def book_search_output(username:str):
    user_folder = os.path.join(Download_dir,username)
    #output.txt has results
    search_result = "results.json"
    with open(os.path.join(user_folder,search_result) , 'r') as json_file:
        return json.load(json_file)
if __name__ == '__main__':
    print("not meant to be ran alone")
    