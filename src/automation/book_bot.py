
import sys,os
from auto_bot_setup import auto_bot
from auto_bot_search import bot_search
from auto_bot_download import start_download
from auto_bot_util import max_limit
#will probably use command line arguments to trigger specific user requested processes
#example "[python] [script_name.py] [search term/phrase] [requester] [settings]""
BOT_SETTINGS = ['getbook', 'getbook-adv', 'pick']

def book_bot():
    if len(sys.argv) != 4:
        print(f'Invalid number of arguments. Expected: 4, Received: {len(sys.argv)}.')
        sys.exit(1)
    if sys.argv[-1] not in BOT_SETTINGS:
        print(f'Invalid setting argument used.')
        sys.exit(1)

    book_search_string = sys.argv[1]
    requester_id = sys.argv[2]
    auto_bot_setting = sys.argv[-1]
    #initialize selenium webdriver 
    bot_driver,user_folder = auto_bot(requester_id)

    #download limit check
    if max_limit(bot_driver):
        print(f'Download limit reached.')
        sys.exit(10)

    outcome = None
    if auto_bot_setting != 'pick':
        bot_search_results = bot_search(bot_driver, book_search_string) # tuple (driver,list of links)
        #can check for tuple or None
        if bot_search_results is None:
            print(f'Error in search scripts.')
            sys.exit(1)

        bot_driver , links = bot_search_results
        if not links:
            print(f'No links can be found for the book.')
            return
        if auto_bot_setting == 'getbook':
            outcome = start_download(bot_driver,user_folder,links[0]) #auto download top link
        elif auto_bot_setting == 'getbook-adv':
            #dump our list of links to output.txt
            try:
                with open(os.path.join(user_folder,"output.txt"), 'w') as f:
                    for items in links:
                        print(items, file= f)
                f.close()
                outcome = True
            except Exception as e:
                print(f'{e}')
    else:
        #its our pick choose/load proper url (?)
        outcome = start_download(bot_driver,user_folder,book_search_string) #bsstring should be direct url
    
    if bot_driver and outcome:
        bot_driver.quit()
        return True
    return None

if __name__ == '__main__':
    book_bot()
