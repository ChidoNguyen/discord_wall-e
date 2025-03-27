import asyncio 
import sys
import json
#from src.automation.book_bot import book_bot
### DO NOT RUN WITH RELOAD ####
system_specific = './myvenv/Scripts/python' if sys.platform == 'win32' else 'python'

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
        return f'{search_title}{search_author}'
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

