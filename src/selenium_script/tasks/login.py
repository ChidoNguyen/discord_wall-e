from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from selenium_script.pages.home_page import HomePage
from src.selenium_script.pages.login_page import LoginPage
from src.selenium_script.pages.download_history import DownloadHistory
from selenium_script.utils.cookies_util import save_cookies

from src.selenium_script.exceptions.homepage import LoginRedirectFailed
from src.selenium_script.exceptions.login_page import LoginPageElementNotFound, LoginProcedureFailed, LoginVerificationError
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

def perform_login(driver : ChromeWebdriver) -> tuple[bool,Exception | None]:

    # Home page check
    home = HomePage(driver)
    if not home.is_home_page():
        return False , NoSuchElementException("Missing home page elements.")
    
    #Navigate and check login page
    login_page_url = home.get_login_url()
    driver.get(login_page_url)
    login_page = LoginPage(driver)
    
    try:
        login_page.is_login_page()
    except LoginPageElementNotFound as e:
        return False, e
    
    # valid login check via cookies loading
    try:
        login_page.valid_login()
        driver.get(config.URL)
        return True , None
    except LoginVerificationError:
        pass #pass here b/c its the initial "are my cookies good" check essentially
    except Exception as e:
        print("Handle unforseen error later")
        return False, e

    # automated manual logging in and refreshing our cookies
    try:
        login_page.perform_login(config.ACCOUNTS[0],config.PASSWORD)
        login_page.valid_login() #only save cookies if login is valid
        _account_pool(driver)
        # XXX PROBABLY NEED TO IMPLEMENT ACC CYCLING LATER 
        save_cookies(driver)
        return True, None
    except (LoginProcedureFailed, LoginVerificationError,CookiesUtilityError) as e:
        return False , e

