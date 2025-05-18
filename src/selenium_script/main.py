import asyncio

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver

from utils.script_status import book_bot_status
from utils.cli_util import parse_arg, direct_script_arg_validation
from utils.webdriver_setup import setup_webdriver
async def book_bot(user: str, search: str, option: str):

    # validates our function arguments
    is_valid, error_msg = direct_script_arg_validation(user=user,search=search,option=option)

    if not is_valid:
        book_bot_status.updates(('Error', f"[Error] [arg validation] : {error_msg}"))
        print(book_bot_status.get_json_output())
        return
    
    bot_webdriver = setup_webdriver(user)
    if not bot_webdriver:
        book_bot_status.updates(("Error", "[Error] [Setup - No webdriver created]"))
        return 
    
    pass

def cli_main():
    user, search, option = parse_arg()
    result = asyncio.run(book_bot(user=user,search=search,option=option))
    return result

if __name__ == '__main__':
    cli_main()

