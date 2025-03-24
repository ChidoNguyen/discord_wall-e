import asyncio 
import sys
#from src.automation.book_bot import book_bot
### DO NOT RUN WITH RELOAD ####
async def find_book_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    discord_user = user_info['username']

    #arguments for book_bot#
    system_specific = './myvenv/Scripts/python' if sys.platform == 'win32' else 'python'
    args = [
        system_specific, '-m',
        'src.automation.book_bot',
        '--search', f'{search_title} by {search_author}',
        '--user', f'{discord_user}',
        '--option', 'getbook'
    ]
    #our process lets call it librarian#
    librarian = await asyncio.create_subprocess_exec(*args,stdout = asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    stdout , stderr = await librarian.communicate()
    print(stdout.decode(),stderr.decode())
    return f'{search_title} by {search_author}'

async def main():
    book_stuff = {
        'title' : 'orign',
        'author' : 'dan brown'
    }
    userr = {'username' : 'mitch'}
    t = await find_book_service(book_stuff,userr)
if __name__ == '__main__':

    asyncio.run(main())