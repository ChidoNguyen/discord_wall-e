from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.common.exceptions import NoSuchElementException

#config
from src.selenium_script.script_config import config_automation as config
#ui/page handlers
from src.selenium_script.pages.home_page import HomePage
from src.selenium_script.pages.login_page import LoginPage
from src.selenium_script.pages.download_history import DownloadHistory
#util
from src.selenium_script.utils.cookies_util import save_cookies
#exceptions
from src.selenium_script.exceptions.login_page import LoginProcedureFailed, LoginVerificationError
from src.selenium_script.exceptions.cookies import CookiesUtilityError
from src.selenium_script.exceptions.download_history import DownloadHistoryElementError

def _account_pool(driver: ChromeWebdriver):
    """ In between logging in and saving cookies, make sure our account is usable due to download limit. """
    dl_hist = DownloadHistory(driver)
    #basic math stuff
    download_count = dl_hist.download_count
    max_download = dl_hist.max_download
    if max_download - download_count <= 0:
        raise LoginProcedureFailed(
            message="Download limit reached"
        )

def _home_page_entry(driver:ChromeWebdriver):
    """
    Initializes our home_page UI handler.

    Args: 
        driver: chrome webdriver instance

    Returns:
        HomePage handler object
    """
    home = HomePage(driver)
    return home , home.is_home_page()

def _get_login_page_handler(driver: ChromeWebdriver, home_handler : HomePage) -> LoginPage:
    login_page_url = home_handler.get_login_url()
    driver.get(login_page_url)
    login_page = LoginPage(driver)
    login_page.is_login_page()
    return login_page

def _validate_cookie_login(driver: ChromeWebdriver, login_page: LoginPage):
    
    try:
        login_page.valid_login()
        driver.get(config.URL) # go back to home page
    except LoginVerificationError:
        return False, None
    except Exception as e:
        return False , e
    return True, None

def _login(driver: ChromeWebdriver, login_page: LoginPage):
    login_page.login(config.ACCOUNTS[0],config.PASSWORD)
    login_page.valid_login()

def perform_login(driver:ChromeWebdriver):
    home_page_handler , valid = _home_page_entry(driver)
    if not valid:
        return False , NoSuchElementException("Missing home page element identifiers.")

    try:
        login_page = _get_login_page_handler(driver, home_page_handler)
    except Exception as e:
        return False, e
    
    login_status , error_msg = _validate_cookie_login(driver,login_page)
    if login_status:
        return True, None
    

    # manual login and update cookies #
    try:
        _login(driver,login_page)
    except (LoginVerificationError,LoginProcedureFailed) as e:
        return False , e 
    
    try:
        save_cookies(driver)
    except CookiesUtilityError as e:
        return False , e 
    
    return True ,None


