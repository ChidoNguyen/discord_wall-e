import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from src.automation.bot_site_cookies import _load_cookies, _save_cookies, _valid_cookies
from .book_bot_config import download_dir , url , userID , userPass

def _create_user_save_dir(requester):
    """
    Function : generates the full path directory for where to save file for this script
    
    Arguments : 
        requester : str - extracted string of username

    Returns : str - the full user path created
    """
    user_folder = os.path.join(download_dir, requester)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder

def _create_auto_bot_driver(save_dir):
    """
    Function : Initiates the selenium webdriver with some predetermined settings/options
    
    Arguments : 
        save_dir : str - the full path to set default saving location for script

    Returns : webdriver 
    """
    #chrome driver options
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless") #no window open during script run
    prefs = {
        "download.default_directory" : save_dir ,
        "savefile.default_directory" : save_dir , 
        "download.prompt_for_download" : False ,
        "directory_upgrade" : True
    }
    options.add_experimental_option('prefs',prefs)
    ###

    bot_driver = None
    if platform.system() == 'Linux': #platform dependent initilization
        service = Service('/usr/bin/chromedriver')
        bot_driver = webdriver.Chrome(service=service , options=options)
    else:
        bot_driver = webdriver.Chrome(options=options)

    return bot_driver

def _get_homepage(bot_driver):
    """
    Function : Navigates to homepage
    
    Arguments : webdriver

    Returns : webdriver  or None
    """
    site_url = url

    bot_driver.get(site_url)
    bot_driver.implicitly_wait(10)
    
    if "Z-Library" in bot_driver.title:
        return bot_driver
    return None

def _login_page(bot_driver):
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
        bot_driver.get(login_link) #navigate to login page
        return bot_driver
    except:
        print(f'Failed to identify link for login page.')
        return None

    #login form
def _login_creds_input(bot_driver):
    """
    Function : Attempts to login with config credentials
    
    Arguments :  webdriver

    Returns : Webdriver or None
    """
    
    uID , uPass = userID , userPass

    login_form = bot_driver.find_element(By.TAG_NAME, "form")
    idEntry = login_form.find_element(By.NAME, 'email').send_keys(uID)
    passEntry = login_form.find_element(By.NAME, 'password').send_keys(uPass)
    submitButton = login_form.find_element(By.TAG_NAME, 'button').click()

    try:
        bot_driver.find_element(By.XPATH, "//a[@href='/logout']")
        return bot_driver
    except:
        print("login attempt failed")
        return None



def create_auto_bot(requester):
    """
    Function : Wrapper function to setup our initial webdriver (login/cookies)
    
    Arguments : 
        requester - str - string of username

    Returns : webdriver or None
    """
    save_dir = _create_user_save_dir(requester)

    ab_driver = _create_auto_bot_driver(save_dir) #setup our initial webdriver client
    homepage_driver = login_element_driver = logged_in_driver = None
    if ab_driver:
        homepage_driver = _get_homepage(ab_driver)

    #cookies check to see if login is needed
    if _valid_cookies():
        _load_cookies(homepage_driver)
        return homepage_driver, save_dir
    else:
        if homepage_driver:
            login_element_driver = _login_page(homepage_driver)
        if login_element_driver:
            logged_in_driver = _login_creds_input(login_element_driver)
        _save_cookies(logged_in_driver)
        return logged_in_driver, save_dir

if __name__ == '__main__':
    create_auto_bot("funz")