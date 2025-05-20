import os
import pickle
import time

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver

from src.selenium_script.script_config import config_automation as config
COOKIES_FILE = "session_state.pkl"
def save_cookies(driver: ChromeWebdriver) -> None:
    try:
        with open(os.path.join(config.COOKIES_DIR,COOKIES_FILE) , 'wb') as file:
            pickle.dump(driver.get_cookies(),file)
    except Exception as e:
        raise RuntimeError("Could not save script cookies.") from e
    
def _is_valid(cookies: list[dict]) -> tuple[bool,str]:
    """ Checks if our session cookies need to be refreshed. """
    if not cookies:
        return False , "No cookies are present."
    cur_time = time.time()

    for cookie in cookies:
        if 'expiry' in cookie and cookie['expiry'] < cur_time:
            return False , "Expired cookies."
    return True , "Valid cookies."

def _inject_cookies(driver:ChromeWebdriver, cookies: list[dict]) -> None:
    ''' injects cookies into our web driver instance '''
    for cookie in cookies:
        driver.add_cookie(cookie)

def _fetch_local_cookies() -> list[dict]:
    ''' Reads in local saved script session cookies/info. '''
    try:
        cookies_path = os.path.join(config.COOKIES_DIR,COOKIES_FILE)
        with open(cookies_path,'rb') as file:
            session_data = pickle.load(file)
        return session_data
    except OSError as e:
        raise RuntimeError("Could not open or locate cookies info file.") from e
    except Exception as e:
        raise RuntimeError("Could not load cookies.") from e
    
def load_cookies(driver: ChromeWebdriver):
    """ TASK : fetches local cookie info , verifies, and injects into webdriver """
    try:
        session_data = _fetch_local_cookies()
        valid_cookies , err_msg = _is_valid(session_data)
        if not valid_cookies:
            print(err_msg)
        _inject_cookies(driver,session_data)
    except Exception as e:
        return
