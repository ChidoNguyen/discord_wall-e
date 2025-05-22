import asyncio

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver

from src.selenium_script.utils.script_status import book_bot_status
from src.selenium_script.utils.cli_util import parse_arg, direct_script_arg_validation
from src.selenium_script.utils.webdriver_setup import setup_webdriver
from selenium_script.utils.cookies_util import load_cookies

from src.selenium_script.tasks.login import perform_login
from src.selenium_script.tasks.job_wrapper import perform_script_option

from src.selenium_script.script_config import config_automation as config

async def book_bot(user: str, search: str, option: str):

    # validates our function arguments
    is_valid, error_msg = direct_script_arg_validation(user=user,search=search,option=option)

    if not is_valid:
        book_bot_status.updates(('Error', f"[Error] [arg validation] : {error_msg}"))
        print(book_bot_status.get_json_output())
        return
    
    bot_webdriver = setup_webdriver(user,headless=False)
    if not bot_webdriver:
        book_bot_status.updates(("Error", "[Error] [Setup - No webdriver created]"))
        return 
    
    #starting point
    bot_webdriver.implicitly_wait(10)
    bot_webdriver.get(config.URL)

    #Cookies
    cookies_status , error_msg = load_cookies(bot_webdriver)
    if not cookies_status:
        #if needed we can log cause
        #tmp = error_msg.__cause___ since we've been chaing exceptions up
        book_bot_status.updates(("Error", f"[Error] [load_cookies] : {error_msg}")) 
        return
    #Login 
    login_status , error_msg = perform_login(bot_webdriver)
    if not login_status:
        book_bot_status.updates(("Error", f"[Error] [perform_login] : {error_msg}")) 
        return
    #Main "jobs" of the script
    job_status , error_msg = perform_script_option() # type: ignore

    pass

def cli_main():#
    user, search, option = parse_arg()
    result = asyncio.run(book_bot(user=user,search=search,option=option))
    return result

if __name__ == '__main__':
    cli_main()

