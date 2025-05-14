
import argparse
import asyncio
from src.automation.auto_bot_setup import create_auto_bot
from src.automation.auto_bot_search import bot_search
from src.automation.auto_bot_download import start_download
from src.automation.auto_bot_util import _check_max_limit , _output_template
from src.automation.book_bot_output import book_bot_status #singleton output handler class

#will probably use command line arguments to trigger specific user requested processes
#example "[python] [script_name.py] [search term/phrase] [requester] [settings]""
BOT_SETTINGS = ['getbook', 'getbook-adv', 'pick']

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
    
    parser.add_argument('--search' , type=str, required=True, help= 'Search string used to designate what to look for.')
    parser.add_argument('--user' , type = str , required= True, help = "User's name to help with file organization and task tracking.")
    parser.add_argument('--option', type = str, required= True, help='Designates the bot for usage type among: getbook , getbook-adv, pick')

    args = parser.parse_args()
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
    book_bot_status.update_step('Download limit check.')
    ### clean up assurance ##
    try:
        outcome = None
        if bot_option != 'pick':
            book_bot_status.update_step('Getbook or Getbook-adv - Entry Point')
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
                    book_bot_status.updates(("Error",f'JSON link output results error : {e}'))
        else:
            book_bot_status.update_step('Pick Option - Attempting to download.')
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

def _direct_script_validation(user:str, search:str, option:str):
    if option not in BOT_SETTINGS:
        book_bot_status.updates(('Error','Invalid option choice.'))
    elif not user.strip():
        book_bot_status.updates(('Error', 'Empty user value.'))
    elif not search.strip():
        book_bot_status.updates(('Error','Empty search value'))
    else:
        return True
    return False

# CLI wrapper + direct callable
async def direct_bot(user : str , search: str , option: str):
    """
    Function : Direct Call to our bot rather than CLI to start automation bot logic

    Arguments: search - string , user - string , option - string
        search - what we want
        user - who wants it
        option - how user wants it
    Returns: None , json formatted bot output reporting tho
    """
    if not _direct_script_validation(user=user,search=search,option=option):
        print(book_bot_status.get_json_output())
        return None
    
    bot_driver, user_folder = create_auto_bot(user)

    if _check_max_limit(bot_driver):
        book_bot_status.updates(('message','Download limit reached. Wait or change accounts'))
        print(book_bot_status.get_json_output())
        bot_driver.quit()
        return None
    book_bot_status.update_step('Download limit check.')
    try:
        outcome = None
        if option == 'pick':
            book_bot_status.update_step('Pick Option - Attempting to download.')
            outcome = start_download(bot_driver,user_folder,search)
        else:
            book_bot_status.update_step("getbook or getbook-adv : Entry point.")
            search_results = bot_search(bot_driver,search)
            if search_results is None:
                book_bot_status.updates(('steps','search'),('message','Error in selenium search script.'))
                print(book_bot_status.get_json_output())
                return None
            
            bot_driver , search_links = search_results
            
            if not search_links:
                book_bot_status.updates(('steps','links acquisition'),('message','No links found.'))
                print(book_bot_status.get_json_output())
                return None
            
            if option == 'getbook':
                outcome = start_download(bot_driver,user_folder,search_links[0])
            elif option == 'getbook-adv':
                try:
                    outcome = _output_template(bot_driver,user_folder,search_links)
                except Exception as e:
                    book_bot_status.updates(("Error",f'JSON link output results error : {e}'))
        if bot_driver and outcome:
            book_bot_status.set_status('success')
            book_bot_status.updates(('message',"successful download"))
            #print(book_bot_status.get_json_output())
        return book_bot_status.get_json_output()
    except Exception as e:
        book_bot_status.updates(('message',e))
        print(book_bot_status.get_json_output())
        return None
    finally:
        if 'bot_driver' in locals() and bot_driver:
            bot_driver.quit()

def book_bot_cli():
    user,search,option = _arg_parse()
    result = asyncio.run(direct_bot(search=search,user=user,option=option))
    return result
if __name__ == '__main__':
    book_bot_cli()
