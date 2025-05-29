import asyncio

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver

from src.selenium_script.utils.script_status import book_bot_status
from src.selenium_script.utils.cli_util import parse_arg, direct_script_arg_validation
from src.selenium_script.utils.webdriver_setup import setup_webdriver
from src.selenium_script.utils.cookies_util import load_cookies

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
    
    bot_webdriver , setup_msg = setup_webdriver(user)
    if not bot_webdriver:
        book_bot_status.updates(("Error", "[Error] [Setup - No webdriver created]"))
        return
    #since setup_msg can be exception or full file path we re-assign to clearer named variable if its a valid driver guard check

    user_download_dir = str(setup_msg)

    #starting point
    bot_webdriver.implicitly_wait(10)
    bot_webdriver.get(config.URL)

    #Cookies
    try:
        load_cookies(bot_webdriver)
    except Exception as e:
        # just a warning since load_cookies is more of a if it works cool less work, if not we'll login and get new cookies anyways
        book_bot_status.updates(("Error", f"[Warning] [load_cookies] : missing expired cookies - {e}")) 
        
    #Login 
    login_status , error_msg = perform_login(bot_webdriver)
    if not login_status:
        book_bot_status.updates(("Error", f"[Error] [perform_login] : {error_msg}"))
        return book_bot_status.get_json_output()

    #Main "jobs" of the script
    job_status , error_msg = perform_script_option(driver=bot_webdriver, download_dir=user_download_dir, search=search,option=option)
    if not job_status:
        book_bot_status.updates(("Error", f"[Error] [Script Job] : {error_msg}"))
        return book_bot_status.get_json_output()
    
    #if successful our error_msg isn't an error message
    if job_status and isinstance(error_msg,dict):
        job_data = error_msg
        book_bot_status.set_status('success')
        book_bot_status.updates(('message','script job success - '))
        #process if we need it
    
    if bot_webdriver and 'bot_webdriver' in locals():
        bot_webdriver.quit()
        
    return book_bot_status.get_json_output()
    #format output text results.

def cli_main():#
    user, search, option = parse_arg()
    result = asyncio.run(book_bot(user=user,search=search,option=option))
    return result
if __name__ == '__main__':
    print(cli_main())

