import os
import pickle
import time

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver

from src.selenium_script.exceptions.cookies import CookiesUtilityError

from src.selenium_script.script_config import config_automation as config

COOKIES_FILE = "session_state.pkl"

def _is_valid(cookies: list[dict]) -> bool:
    """ Checks if our session cookies need to be refreshed. """
    if not cookies:
        raise CookiesUtilityError(
            message= "Cookies are empty or missing.",
            action= "._is_valid parameter passing."
        )

    cur_time = time.time()

    for cookie in cookies:
        if 'expiry' in cookie and cookie['expiry'] < cur_time:
            raise CookiesUtilityError(
                message="Cookies are expired."
            )
    return True

def _inject_cookies(driver:ChromeWebdriver, cookies: list[dict]) -> None:
    ''' 
    injects cookies into our web driver instance 

    Args:
        list containing our cookies, each cookie is a dictionary object.

    Returns:
        None
    '''
    for cookie in cookies:
        driver.add_cookie(cookie)

def _fetch_local_cookies() -> list[dict]:
    ''' 
    Reads in local saved script session cookies/info. 
    
    Args: None

    Returns:
        list[dict] a list container of cookies (dict) values
    '''
    cookies_path = os.path.join(config.COOKIES_DIR,COOKIES_FILE)
    with open(cookies_path,'rb') as file:
        session_data = pickle.load(file)
    return session_data
    
    
def load_cookies(driver: ChromeWebdriver) -> None:
    """ TASK : fetches local cookie info , verifies, and injects into webdriver 
    
    """
    session_data = _fetch_local_cookies()
    if _is_valid(session_data):
        _inject_cookies(driver,session_data)
    
    

def save_cookies(driver: ChromeWebdriver) -> tuple[bool,Exception| None]:
    """ Saves  cookies we currently have in selenium chrome driver to a pickle file. """

    # redirect cookie expires fast - filter out
    all_cookies = driver.get_cookies()
    filtered_cookies = [
        cookie for cookie in all_cookies
        if cookie.get('name') != 'redirects_count' and 'expiry' in cookie
    ]
    try:
        with open(os.path.join(config.COOKIES_DIR,COOKIES_FILE) , 'wb') as file:
            pickle.dump(filtered_cookies,file)
        return True, None
    except Exception as e:
        # new exception to maintain "task" level returns are bool,[Exception or str]
        new_exception = RuntimeError("Could not save script cookies.")
        new_exception.__cause__ = e
        return False, new_exception
   