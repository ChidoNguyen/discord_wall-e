import asyncio
#from src.automation.book_bot import book_bot


async def find_book_service(book_info : dict, user_info : dict):
    search_title = book_info['title']
    search_author = book_info['author']
    discord_user = user_info['username']

    #arguments for book_bot#
    args = [
        'python', '-m',
        'src.automation.book_bot',
        '--search', f'{search_title} by {search_author}',
        '--user', f'{discord_user}',
        '--option', 'getbook'
    ]
    #our process lets call it librarian#
    print("start")
    librarian = await asyncio.create_subprocess_exec(*args,stdout = asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    stdout , stderr = await librarian.communicate()
    #print(stdout.decode(),stderr.decode())
    tmp = {
        'status' : 'success',
        'message' : 'selenium script success',
        'file_path' : 'none'
    }
    return f'{search_title} by {search_author}'

'''
import asyncio

async def run_selenium_script():
    # Define the command-line arguments to run the Selenium script
    args = [
        "python", "-m", "src.module.file",  # Path to your Selenium script
        "--a", "A",                        # Command-line argument 1
        "--b", "B",                        # Command-line argument 2
        "--c", "C"                         # Command-line argument 3
    ]
    
    # Run the Selenium script asynchronously using asyncio
    process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    # Capture the output and error (if any)
    stdout, stderr = await process.communicate()

    if stderr:
        return f"Error: {stderr.decode()}"
    
    return stdout.decode()

'''