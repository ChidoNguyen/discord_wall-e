
import argparse
import json
from src.automation.auto_bot_setup import create_auto_bot
from src.automation.auto_bot_search import bot_search
from src.automation.auto_bot_download import start_download
from src.automation.auto_bot_util import _check_max_limit , _output_template
from src.automation.book_bot_output import book_bot_status #singleton output handler class

#will probably use command line arguments to trigger specific user requested processes
#example "[python] [script_name.py] [search term/phrase] [requester] [settings]""
BOT_SETTINGS = ['getbook', 'getbook-adv', 'pick']
JOB_STATUS_OUTPUT = {
    'status' : 'initialization',
    'metadata' : None,
    'message' : None,
    'job stage' : None
}
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
    book_bot_status.updates(('steps', 'arg parse'))
    
    if None in (bot_search_terms,bot_username,bot_option) or bot_option not in BOT_SETTINGS:
        book_bot_status.updates(('message','invalid argument(s)'))
        print(book_bot_status.get_json_output())
        return None

    #bot options check
    """ if bot_option not in BOT_SETTINGS:
        print(json.dumps({"status" : "failure" , "message" : "Invalid bot option."}))
        return None """

    #initialize selenium webdriver
    bot_driver,user_folder = create_auto_bot(bot_username)

    #download limit check
    if _check_max_limit(bot_driver):
        book_bot_status.updates(('message','Download limit reached. Wait or change accounts'))
        print(book_bot_status.get_json_output())
        bot_driver.quit()
        return None
    book_bot_status.updates(('steps','WebDriver active'))
    ### clean up assurance ##
    try:
        outcome = None
        if bot_option != 'pick':
            bot_search_results = bot_search(bot_driver, bot_search_terms) # tuple (driver,list of links)
            #can check for tuple or None
            if bot_search_results is None:
                book_bot_status.updates(('steps','search'),('message','Error in selenium search script'))
                print(book_bot_status.get_json_output())
                return None

            bot_driver , links = bot_search_results
            if not links:
                book_bot_status.updates(('steps','links acquisition'),('message','No links found.'))
                print(book_bot_status.get_json_output())
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
            book_bot_status.set_status('success')
            book_bot_status.updates(('message', 'Successful download'))
            print(book_bot_status.get_json_output())
        return None
    
    except Exception as e:
        book_bot_status.updates(('message',e))
        print(book_bot_status.get_json_output())
        return None
    finally:
        #### for debugging ####
        #logs = bot_driver.get_log("browser")
        #for entry in logs:
        #    print(f"{entry['level']} - {entry['message']}")
        ####
        if 'bot_driver' in locals() and bot_driver:
            bot_driver.quit()


if __name__ == '__main__':
    book_bot()
