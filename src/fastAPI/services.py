import asyncio 
import sys
import json
import os
import shutil
import sqlite3
import time
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
async def find_book_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    discord_user = user_info['username']

    #arguments for book_bot#
    args = [
        system_specific, '-m',
        'src.automation.book_bot',
        '--search', f'{search_title} {search_author}',
        '--user', f'{discord_user}',
        '--option', 'getbook'
    ]
    #our process lets call it librarian#
    librarian = await asyncio.create_subprocess_exec(*args,stdout = asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    
    try:
        stdout , stderr = await asyncio.wait_for(librarian.communicate(),timeout=90)
    except asyncio.TimeoutError:
        print("find_book_service terminated for taking too long")
        return None
    #print(stdout.decode(),stderr.decode())
    stdout_decode = stdout.decode()
    #stderr_decode = stderr.decode()
    result = json.loads(stdout_decode)
    if result.get('status') == 'success':
        return result
    return None # assuming if not success then failure

########
async def find_book_service_roids(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    discord_user = user_info['username']

    #arguments for book_bot#
    args = [
        system_specific, '-m',
        'src.automation.book_bot',
        '--search', f'{search_title} {search_author}',
        '--user', f'{discord_user}',
        '--option', 'getbook-adv'
    ]
    #our process lets call it librarian#
    librarian = await asyncio.create_subprocess_exec(*args,stdout = asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    
    try:
        stdout , stderr = await asyncio.wait_for(librarian.communicate(),timeout=90)
    except asyncio.TimeoutError:
        print("find_book_service_on_roid terminated for taking too long")
        return None
    stdout_decode = stdout.decode()
    #stderr_decode = stderr.decode()
    result = json.loads(stdout_decode)
    if result.get('status') == 'success':
        return f'{search_title} {search_author}'
    return None # assuming if not success then failure

async def find_book_options(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    discord_user = user_info['username']

    #arguments for book_bot#
    args = [
        system_specific, '-m',
        'src.automation.book_bot',
        '--search', f'{search_title} {search_author}',
        '--user', f'{discord_user}',
        '--option', 'pick'
    ]
    #our process lets call it librarian#
    librarian = await asyncio.create_subprocess_exec(*args,stdout = asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    
    try:
        stdout , stderr = await asyncio.wait_for(librarian.communicate(),timeout=90)
    except asyncio.TimeoutError:
        print("find_book_option - terminated for taking too long")
        return None
    #print(stdout.decode(),stderr.decode())
    stdout_decode = stdout.decode()
    #stderr_decode = stderr.decode()
    result = json.loads(stdout_decode)
    if result.get('status') == 'success':
        return result
    return None # assuming if not success then failure    

async def _create_database_job(job_details):
    '''
    Params : Dictionary of info needed to do the job source path / author / title/ username
        source : str - full path to where the finished file is residing
        author / title : str - used to format new file name during job
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
        shutil.move(newest_file,THE_VAULT)
    finally:
        return
async def _register_vault(job_details):
    source,title,author,username = job_details.values()
    #db#
    db_con = sqlite3.connect(DB_PATH)
    cursor = db_con.cursor()
    sql_insert_ignore = "INSERT OR IGNORE INTO digital_brain (title,author,user) VALUES (?,?,?)"
    cursor.execute(sql_insert_ignore,(title,author,username))
    #print(cursor.execute("SELECT * FROM digital_brain").fetchall())
    db_con.commit()
    db_con.close()
    ###

    if os.path.exists(source):
        try:
            moved_path = shutil.move(source,os.path.join(THE_VAULT,f'{title} by {author}.epub'))
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
    