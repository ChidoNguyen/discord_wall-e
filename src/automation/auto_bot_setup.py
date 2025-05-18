import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from src.automation.bot_site_cookies import _load_cookies, _save_cookies, _valid_cookies
#from .book_bot_config import download_dir , url , userID , userPass
##### 
from src.automation.script_config import config_automation as config
#####
from src.automation.book_bot_output import book_bot_status

def _create_user_save_dir(requester: str) -> str | None:
    """
    Function : generates the full path directory for where to save file for this script
    
    Arguments : 
        requester : str - extracted string of username

    Returns : str - the full user path created
    """
    from src.env_config import config as src_config
    book_bot_status.update_step("create user save dir")
    try:
        user_folder = os.path.join(src_config.DOWNLOAD_DIR, requester)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        return user_folder
    except Exception as e:
        book_bot_status.updates(('Error',f'create_user_save_dir - {e}'))
        return None

def _create_auto_bot_driver(save_dir : str) ->ChromeWebdriver | None:
    """
    Function : Initiates the selenium webdriver with some predetermined settings/options
    
    Arguments : 
        save_dir : str - the full path to set default saving location for script

    Returns : webdriver 
    """
    book_bot_status.update_step('create webdriver')
    #chrome driver options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") #no window open during script run
    ##### NEW RESOURCE OPTIONS (?) ######

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,800")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--safebrowsing-disable-auto-update")
    options.add_argument("--disable-blink-features=AutomationControlled")



    #######
    prefs = {
        "download.default_directory" : save_dir ,
        "savefile.default_directory" : save_dir , 
        "download.prompt_for_download" : False ,
        "directory_upgrade" : True,
        "profile.managed_default_content_settings.images": 2 #new
    }
    options.add_experimental_option('prefs',prefs)
    ### debug logging ###
    #options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    ###
    bot_driver = None
    try:
        if platform.system() == 'Linux': #platform dependent initilization
            service = Service('/usr/bin/chromedriver')
            bot_driver = webdriver.Chrome(service=service , options=options)
        else:
            bot_driver = webdriver.Chrome(options=options)
    except Exception as e:
        book_bot_status.updates(('Error',f'create_auto_bot_driver - {e}'))
    return bot_driver

def _get_homepage(bot_driver: ChromeWebdriver) -> ChromeWebdriver | None:
    """
    Function : Navigates to homepage
    
    Arguments : webdriver

    Returns : webdriver  or None
    """
    site_url = config.URL
    bot_driver.get(site_url)
    bot_driver.implicitly_wait(10)
    
    if config.TARGET_TITLE in bot_driver.title:
        return bot_driver
    return None

def _login_page(bot_driver : ChromeWebdriver) -> ChromeWebdriver | None:
    """
    Function : Navigates to login page
    
    Arguments : webdriver

    Returns : webdriver or None
    """
    login_html_text = {
        'login-div' : 'user-data__sign',

    }
    #login page link
    try:
        login_link_div = bot_driver.find_element(By.CLASS_NAME , login_html_text['login-div'])
        anchor_element = login_link_div.find_element(By.TAG_NAME, 'a')
        login_link = anchor_element.get_attribute('href')
    except Exception as e:
        book_bot_status.updates(('Error' , f'Login page error - {e}'))
        return None
    
    if login_link:
        return bot_driver.get(login_link)
    else:
        return None

    #login form
def _login_creds_input(bot_driver: ChromeWebdriver) -> ChromeWebdriver | None:
    """
    Function : Attempts to login with config credentials
    
    Arguments :  webdriver

    Returns : Webdriver or None
    """
    
    uID , uPass = config.ACCOUNTS[0] , config.PASSWORD

    login_form = bot_driver.find_element(By.TAG_NAME, "form")
    idEntry = login_form.find_element(By.NAME, 'email').send_keys(uID)
    passEntry = login_form.find_element(By.NAME, 'password').send_keys(uPass)
    submitButton = login_form.find_element(By.TAG_NAME, 'button').click()

    try:
        bot_driver.find_element(By.XPATH, "//a[@href='/logout']")
        return bot_driver
    except Exception as e:
        book_bot_status.updates(('Error',f'Login attempt failed - {e}'))
        return None



def create_auto_bot(requester : str) -> tuple[ChromeWebdriver | None, str | None]:
    """
    Function : Wrapper function to setup our initial webdriver (login/cookies)
    
    Arguments : 
        requester - str - string of username

    Returns : webdriver or None
    """
    save_dir = _create_user_save_dir(requester)
    if save_dir is None:
        return None , None
    ab_driver = _create_auto_bot_driver(save_dir) #setup our initial webdriver client
    homepage_driver = login_element_driver = logged_in_driver = None
    if ab_driver:
        homepage_driver = _get_homepage(ab_driver)

    #cookies check to see if login is needed
    if _valid_cookies() and homepage_driver:
        book_bot_status.update_step('Cookies login')
        _load_cookies(homepage_driver)
        return homepage_driver, save_dir
    else:
        book_bot_status.update_step('New login + refresh cookies')
        if homepage_driver:
            login_element_driver = _login_page(homepage_driver)
        if login_element_driver:
            logged_in_driver = _login_creds_input(login_element_driver)
        if logged_in_driver:
            _save_cookies(logged_in_driver)
        return logged_in_driver, save_dir

if __name__ == '__main__':
    create_auto_bot("funz")