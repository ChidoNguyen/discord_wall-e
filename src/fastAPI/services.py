import asyncio 
import sys
import json
import os
import shutil
import sqlite3
import time
from src.automation.book_bot import direct_bot
from src.fastAPI.catalog_cache import get_cache_data
from dotenv import load_dotenv
#from src.automation.book_bot import book_bot
load_dotenv()
THE_VAULT = os.getenv('THE_VAULT')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
THE_JOBS = os.getenv('THE_JOBS')
DB_PATH = os.getenv('DB_PATH')
### DO NOT RUN WITH RELOAD ####
system_specific = './myvenv/Scripts/python' if sys.platform == 'win32' else 'python'
'''
Selenium Script Formatted Output (JSON):
    status : str
    metadata : None | JSON(source/title/author/username)
    message : None | str
    steps : list
    misc : list
'''
async def find_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    user = user_info['username']
    search = f'{search_title} {search_author}'
    #arguments for book_bot#
    script_results = await direct_bot(user=user,search=search,option='getbook')

    if script_results:
        try:
            script_result_parse = json.loads(script_results)
            if script_result_parse.get('status') == 'success':
                return {
                    'message' : script_result_parse.get('message'), 'metadata' : script_result_parse.get('metadata')
                    }
        except Exception as e:
            print(e)
            pass
    return None

########
async def find_hardmode_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    user = user_info['username']
    search = f'{search_title} {search_author}'
    #arguments for book_bot#
    script_results = await direct_bot(user=user,search=search,option='getbook-adv')

    if script_results:
        try:
            script_results_parse = json.loads(script_results)
            if script_results_parse.get('status') == 'success':
                return {
                    'message': 'found some results',
                    'metadata' : []
                    }
        except Exception as e:
            print(e)
            pass
    return None

async def pick_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    user = user_info['username']
    search = f'{search_title} {search_author}'

    script_results = await direct_bot(user=user,search=search,option='pick')

    if script_results:
        try:
            script_results_parse = json.loads(script_results)
            if script_results_parse.get('status') == 'success':
                return {
                    'message' : script_results_parse.get('message'),
                    'metadata' : script_results_parse.get('metadata')
                }
        except Exception as e:
            print(e)
            pass
    return None
  
async def catalog_service():
    return get_cache_data()

def holder():
    cache_info_path = os.path.join(THE_VAULT,'cache')
    catalog_info_file = 'cache_info.json'
    catalog_cache_path = os.path.join(cache_info_path,catalog_info_file)
    with open(catalog_cache_path) as file:
        tmp =file.read()
    print(tmp)

async def _create_database_job(job_details):
    '''
    Params : Dictionary of info needed to do the job source path / author / title/ username
        source : str - full path to where the finished file is residing
        author : str
        fname : str
        lname : str
        title : str 
        username : str - for catalog purposes
    Output : json job file will be created in env. defined directory 
    '''
    username = job_details['username']
    job_file_name = f'{username}_book_{int(time.time())}.json'
    with open(os.path.join(THE_JOBS,job_file_name),'w') as f:
        json.dump(job_details,f)
    return job_file_name


""" async def metadata_extraction(book):
    from ebooklib import epub

    ebook = epub.read_epub(book)
    author = ebook.get_metadata('DC','creator')[0][0]
    title = ebook.get_metadata('DC', 'title')[0][0]

    return { 'author' : author , 'title' : title}
 """
async def to_the_vault(user):
    #get the newest file in folder 
    #move to the vault
    try:
        userfolder = os.path.join(DOWNLOAD_DIR,user)
        dir_files = []
        for files in os.listdir(userfolder):
            dir_files.append(os.path.join(userfolder,files))
        newest_file = max(dir_files,key=os.path.getctime)
        shutil.move(newest_file,os.path.join(THE_VAULT,'the_goods'))
    finally:
        return
async def _register_vault(job_details):
    #all are expected to be present direct access for error raising
    source = job_details['source']
    aut_fname = job_details['fname']
    aut_lname = job_details['lname']
    title = job_details['title']
    username = job_details['username']
    #db#
    db_con = sqlite3.connect(DB_PATH)
    cursor = db_con.cursor()
    sql_insert_ignore = "INSERT OR IGNORE INTO digital_brain (title,author_first_name,author_last_name,user) VALUES (?,?,?,?)"
    cursor.execute(sql_insert_ignore,(title,aut_fname,aut_lname,username))
    #print(cursor.execute("SELECT * FROM digital_brain").fetchall())
    db_con.commit()
    db_con.close()
    ###
    author = f'{aut_fname} {aut_lname}'.strip()
    if os.path.exists(source):
        try:
            moved_path = shutil.move(source,os.path.join(os.path.join(THE_VAULT,'the_goods'),f'{title} by {author}.epub'))
            return True , moved_path
        except Exception as e:
            return False,f'Error shutil.move() - {e}'
    return False, None

            

async def cron_fake(job_details):
    await _create_database_job(job_details)
    job_listings = [os.path.join(THE_JOBS,files) for files in os.listdir(THE_JOBS) if files.endswith('json')]
    for items in job_listings:
        with open(items, 'r') as f:
            job_info = json.load(f)
            status, data = await _register_vault(job_info)
        if status and os.path.exists(data):
            os.remove(items)
        #if data is not None:
        #    print(data)
        if status is False and data is not None:
            print(data)
    return
    