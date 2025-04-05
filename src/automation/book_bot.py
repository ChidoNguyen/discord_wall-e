
import argparse
import json
from src.automation.auto_bot_setup import create_auto_bot
from src.automation.auto_bot_search import bot_search
from src.automation.auto_bot_download import start_download
from src.automation.auto_bot_util import _check_max_limit , _output_template
#will probably use command line arguments to trigger specific user requested processes
#example "[python] [script_name.py] [search term/phrase] [requester] [settings]""
BOT_SETTINGS = ['getbook', 'getbook-adv', 'pick']
'''
diff system argument approach from ORDER dependent arguments to
anyorder via keyword arguments

--search
--user
--option

'''
def _arg_parse():
    """
    Function : Parses our command line argument
    
    Arguments : COMMAND LINE ARGUMENTS
        --search : str : full search query
        --user : str : username
        --option : str : getbook / getbook-adv / pick

    Returns : parsed args or None(s)
    """
    parser = argparse.ArgumentParser(description="book_bot_kwargs")
    #argument count 
    count = 3

    parser.add_argument('--search' , type=str, required=True, help= 'Search string used to designate what to look for.')
    parser.add_argument('--user' , type = str , required= True, help = "User's name to help with file organization and task tracking.")
    parser.add_argument('--option', type = str, required= True, help='Designates the bot for usage type among: getbook , getbook-adv, pick')
    try:
        args = parser.parse_args()
    except:
        return (None,) * count
    return args.user, args.search, args.option

def book_bot():
    """
    Function : Our main "automation" bot logic
    
    Arguments : Command line arguments --option , --user , --search 

    Returns : prints formatted messages as a form of "return" but essentially returns None and shuts down selenium driver. 
    """
    #keyword arg parsing rather than positional args
    bot_username, bot_search_terms,bot_option = _arg_parse()


    if None in (bot_search_terms,bot_username,bot_option):
        #print(f'Invalid number of arguments')
        tmp = {"status" : "failure" , "message" : "Invalid arguments"}
        print(json.dumps(tmp))
        return None

    #bot options check
    if bot_option not in BOT_SETTINGS:
        print(json.dumps({"status" : "failure" , "message" : "Invalid bot option."}))
        return None

    #initialize selenium webdriver
    bot_driver,user_folder = create_auto_bot(bot_username)

    #download limit check
    if _check_max_limit(bot_driver):
        print(json.dumps({"status" : "failure" , "message" : "Download Limit Reached (wait or change accounts)."}))
        bot_driver.quit()
        return None

    ### clean up assurance ##
    try:
        outcome = None
        if bot_option != 'pick':
            bot_search_results = bot_search(bot_driver, bot_search_terms) # tuple (driver,list of links)
            #can check for tuple or None
            if bot_search_results is None:
                print(json.dumps({"status" : "failure" , "message" : "Error in selenium search script"}))
                return None

            bot_driver , links = bot_search_results
            if not links:
                print(json.dumps({"status" : "failure" , "message" : "No links found for search query."}))
                return None
            if bot_option == 'getbook':
                outcome = start_download(bot_driver,user_folder,links[0]) #auto download top link
            elif bot_option == 'getbook-adv':
                #dump our list of links to output.txt
                try:
                    ###
                    _output_template(bot_driver,user_folder,links)
                    outcome = True
                except Exception as e:
                    print(f'{e}')
        else:
            #its our pick choose/load proper url (?)
            outcome = start_download(bot_driver,user_folder,bot_search_terms) #bsstring should be direct url
        
        if bot_driver and outcome:
            print(json.dumps({'status' : 'success' , 'message' : 'book found'}))
        return None
    
    except Exception as e:
        print(json.dumps({'status':'failure' , 'message' : e}))
        return None
    finally:
        if 'bot_driver' in locals() and bot_driver:
            bot_driver.quit()


if __name__ == '__main__':
    book_bot()
